"""API integration tests for CRUD + redirect using async httpx client."""

import httpx
import pytest
import pytest_asyncio

from src.api.app import app


@pytest_asyncio.fixture(name="client")
async def _client_fixture(monkeypatch: pytest.MonkeyPatch) -> httpx.AsyncClient:
    """Provide an AsyncClient with ASGITransport; DB path via shared conftest."""
    monkeypatch.setenv("BASE_URL", "http://testserver")
    monkeypatch.delenv("EDIT_TOKEN_PEPPER", raising=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_then_update_and_delete_flow(client: httpx.AsyncClient) -> None:
    """Create a link, update with valid token, then delete with same token."""
    # Create link
    r = await client.post(
        "/api/links",
        json={"target_url": "https://example.com/x", "redirect_code": 301},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    link_id = data["link_id"]
    token = data["edit_token"]

    # Update target_url with token header
    r = await client.patch(
        f"/api/links/{link_id}",
        headers={"X-Edit-Token": token},
        json={"target_url": "https://example.com/updated"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["target_url"].endswith("/updated")

    # Delete with token header
    r = await client.delete(f"/api/links/{link_id}", headers={"X-Edit-Token": token})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_conflict_on_custom_id(client: httpx.AsyncClient) -> None:
    """Creating two links with same custom alias returns 409 on second try."""
    # Create with custom id
    payload = {
        "target_url": "https://example.com/a",
        "link_id": "MyAlias",
        "redirect_code": 301,
    }
    r1 = await client.post("/api/links", json=payload)
    assert r1.status_code == 200

    # Second with same id should 409
    r2 = await client.post("/api/links", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_update_requires_token(client: httpx.AsyncClient) -> None:
    """PATCH requires X-Edit-Token and returns 401 without it."""
    r = await client.post("/api/links", json={"target_url": "https://example.com/"})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    r2 = await client.patch(f"/api/links/{link_id}", json={"target_url": "https://example.com/y"})
    assert r2.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_on_delete(client: httpx.AsyncClient) -> None:
    """DELETE with wrong token returns 403."""
    r = await client.post("/api/links", json={"target_url": "https://example.com/"})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    r2 = await client.delete(f"/api/links/{link_id}", headers={"X-Edit-Token": "bad"})
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_redirect_permanent_cache_headers(client: httpx.AsyncClient) -> None:
    """Permanent redirects (301/308) should set cache headers with max-age and immutable."""
    # Create link with 301
    r = await client.post(
        "/api/links",
        json={
            "target_url": "https://example.com/perma",
            "redirect_code": 301,
        },
    )
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    resp = await client.get(f"/{link_id}", follow_redirects=False)
    assert resp.status_code == 301
    cc = resp.headers.get("Cache-Control", "")
    assert "max-age=" in cc and "immutable" in cc
    assert resp.headers.get("Location") == "https://example.com/perma"


@pytest.mark.asyncio
async def test_redirect_temporary_no_store(client: httpx.AsyncClient) -> None:
    """Temporary redirects (302/307) should be non-cacheable (no-store)."""
    r = await client.post(
        "/api/links",
        json={
            "target_url": "https://example.com/temp",
            "redirect_code": 302,
        },
    )
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    resp = await client.get(f"/{link_id}", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers.get("Cache-Control") == "no-store"
    assert resp.headers.get("Location") == "https://example.com/temp"


@pytest.mark.asyncio
async def test_redirect_deleted_returns_410(client: httpx.AsyncClient) -> None:
    """Deleted link returns 410 Gone."""
    r = await client.post("/api/links", json={"target_url": "https://example.com/del"})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    # Delete
    token = r.json()["edit_token"]
    del_resp = await client.delete(f"/api/links/{link_id}", headers={"X-Edit-Token": token})
    assert del_resp.status_code == 200
    # Test redirect after deletion
    resp = await client.get(f"/{link_id}", follow_redirects=False)
    assert resp.status_code == 410


@pytest.mark.asyncio
async def test_redirect_not_found_404(client: httpx.AsyncClient) -> None:
    """Unknown link id returns 404."""
    resp = await client.get("/no-such-id", follow_redirects=False)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_head_redirect_returns_headers_only(client: httpx.AsyncClient) -> None:
    """HEAD should return same status and headers without body."""
    r = await client.post(
        "/api/links",
        json={
            "target_url": "https://example.com/head",
            "redirect_code": 308,
        },
    )
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    resp = await client.head(f"/{link_id}", follow_redirects=False)
    assert resp.status_code == 308
    assert resp.headers.get("Location") == "https://example.com/head"


@pytest.mark.asyncio
async def test_alias_change_tombstones_old_alias(client: httpx.AsyncClient) -> None:
    """Changing alias should make old alias return 410 and new alias redirect."""
    # Create link
    r = await client.post(
        "/api/links",
        json={
            "target_url": "https://example.com/alias",
            "redirect_code": 302,
            "link_id": "OldAlias",
        },
    )
    assert r.status_code == 200
    token = r.json()["edit_token"]
    old_id = r.json()["link_id"]

    # Change alias
    patch_resp = await client.patch(
        f"/api/links/{old_id}",
        headers={"X-Edit-Token": token},
        json={"new_link_id": "NewAlias"},
    )
    assert patch_resp.status_code == 200
    new_id = patch_resp.json()["link_id"]
    assert new_id == "newalias"  # normalized lower-case

    # Old alias should be tombstoned: 410
    old_redirect = await client.get(f"/{old_id}", follow_redirects=False)
    assert old_redirect.status_code == 410

    # New alias should redirect
    new_redirect = await client.get(f"/{new_id}", follow_redirects=False)
    assert new_redirect.status_code == 302
    assert new_redirect.headers.get("Location") == "https://example.com/alias"
