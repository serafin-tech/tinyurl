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
