"""API integration tests for CRUD endpoints using TestClient."""

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture(name="client")
def _client_fixture(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Provide a TestClient with base URL set; DB path provided via shared conftest."""
    # Only set base URL and ensure no pepper unless set by environment
    monkeypatch.setenv("BASE_URL", "http://testserver")
    monkeypatch.delenv("EDIT_TOKEN_PEPPER", raising=False)
    return TestClient(app)


def test_create_then_update_and_delete_flow(client: TestClient) -> None:
    """Create a link, update with valid token, then delete with same token."""
    # Create link
    r = client.post(
        "/api/links",
        json={"target_url": "https://example.com/x", "redirect_code": 301},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    link_id = data["link_id"]
    token = data["edit_token"]

    # Update target_url with token header
    r = client.patch(
        f"/api/links/{link_id}",
        headers={"X-Edit-Token": token},
        json={"target_url": "https://example.com/updated"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["target_url"].endswith("/updated")

    # Delete with token header
    r = client.delete(f"/api/links/{link_id}", headers={"X-Edit-Token": token})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "deleted"


def test_conflict_on_custom_id(client: TestClient) -> None:
    """Creating two links with same custom alias returns 409 on second try."""
    # Create with custom id
    payload = {
        "target_url": "https://example.com/a",
        "link_id": "MyAlias",
        "redirect_code": 301,
    }
    r1 = client.post("/api/links", json=payload)
    assert r1.status_code == 200

    # Second with same id should 409
    r2 = client.post("/api/links", json=payload)
    assert r2.status_code == 409


def test_update_requires_token(client: TestClient) -> None:
    """PATCH requires X-Edit-Token and returns 401 without it."""
    r = client.post("/api/links", json={"target_url": "https://example.com/"})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    r2 = client.patch(f"/api/links/{link_id}", json={"target_url": "https://example.com/y"})
    assert r2.status_code == 401


def test_invalid_token_on_delete(client: TestClient) -> None:
    """DELETE with wrong token returns 403."""
    r = client.post("/api/links", json={"target_url": "https://example.com/"})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    r2 = client.delete(f"/api/links/{link_id}", headers={"X-Edit-Token": "bad"})
    assert r2.status_code == 403


def test_redirect_permanent_cache_headers(client: TestClient) -> None:
    """Permanent redirects (301/308) should set cache headers with max-age and immutable."""
    # Create link with 301
    r = client.post("/api/links", json={"target_url": "https://example.com/perma", "redirect_code": 301})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    resp = client.get(f"/{link_id}", allow_redirects=False)
    assert resp.status_code == 301
    cc = resp.headers.get("Cache-Control", "")
    assert "max-age=" in cc and "immutable" in cc
    assert resp.headers.get("Location") == "https://example.com/perma"


def test_redirect_temporary_no_store(client: TestClient) -> None:
    """Temporary redirects (302/307) should be non-cacheable (no-store)."""
    r = client.post("/api/links", json={"target_url": "https://example.com/temp", "redirect_code": 302})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    resp = client.get(f"/{link_id}", allow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers.get("Cache-Control") == "no-store"
    assert resp.headers.get("Location") == "https://example.com/temp"


def test_redirect_deleted_returns_410(client: TestClient) -> None:
    """Deleted link returns 410 Gone."""
    r = client.post("/api/links", json={"target_url": "https://example.com/del"})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    # Delete
    token = r.json()["edit_token"]
    del_resp = client.delete(f"/api/links/{link_id}", headers={"X-Edit-Token": token})
    assert del_resp.status_code == 200
    # Test redirect after deletion
    resp = client.get(f"/{link_id}", allow_redirects=False)
    assert resp.status_code == 410


def test_redirect_not_found_404(client: TestClient) -> None:
    """Unknown link id returns 404."""
    resp = client.get("/no-such-id", allow_redirects=False)
    assert resp.status_code == 404


def test_head_redirect_returns_headers_only(client: TestClient) -> None:
    """HEAD should return same status and headers without body."""
    r = client.post("/api/links", json={"target_url": "https://example.com/head", "redirect_code": 308})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    resp = client.head(f"/{link_id}", allow_redirects=False)
    assert resp.status_code == 308
    assert resp.headers.get("Location") == "https://example.com/head"
