"""FastAPI application entrypoint for TinyURL Backend MVP."""

from dataclasses import asdict
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.adapters.db.repository import LinkRepository
from src.api.deps import (
    get_base_url,
    get_db,
    get_edit_token,
    get_permanent_cache_seconds,
    get_token_pepper,
)
from src.api.schemas import (
    CreateLinkRequest,
    CreateLinkResponse,
    LinkOut,
    UpdateLinkRequest,
)
from src.domain.errors import ConflictError, NotFoundError, ValidationError
from src.domain.id_token import (
    generate_edit_token,
    generate_unique_link_id,
    hash_token,
    verify_token,
)
from src.domain.validators import (
    normalize_link_id,
    normalize_url,
    validate_link_id,
    validate_redirect_code,
)

app = FastAPI(title="TinyURL Backend MVP", version="0.1.0")


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.api_route("/{link_id}", methods=["GET", "HEAD"])
async def redirect_link(
    link_id: str,
    db: Session = Depends(get_db),
    permanent_cache_seconds: int = Depends(get_permanent_cache_seconds),
):
    """Redirect to the target URL based on stored link configuration.

    Returns 404 if link not found, 410 if deleted or expired. Applies cache headers:
    - 301/308: Cache-Control with max-age (configurable) & immutable hint
    - 302/307: no-store
    """
    repo = LinkRepository(db)
    try:
        link = repo.get(link_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="not found") from exc

    # Deleted or inactive
    if not link.active:
        raise HTTPException(status_code=410, detail="gone")
    # Expired
    if link.expires_at and link.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=410, detail="gone")

    headers: dict[str, str] = {}
    if link.redirect_code in (301, 308):
        headers["Cache-Control"] = f"public, max-age={permanent_cache_seconds}, immutable"
    else:
        headers["Cache-Control"] = "no-store"
    return RedirectResponse(
        url=link.target_url,
        status_code=link.redirect_code,
        headers=headers
    )


@app.exception_handler(ValidationError)
async def handle_validation_error(
    _req: Request, exc: ValidationError
) -> JSONResponse:
    """Map domain ValidationError to HTTP 400 JSON response."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.post("/api/links", response_model=CreateLinkResponse)
async def create_link(
    payload: CreateLinkRequest,
    db: Session = Depends(get_db),
    base_url: str = Depends(get_base_url),
    pepper: str | None = Depends(get_token_pepper),
) -> CreateLinkResponse:
    """Create a new short link, generating a unique id and edit token when needed."""
    repo = LinkRepository(db)

    # Validate and normalize inputs
    target_url = normalize_url(payload.target_url)
    redirect_code = payload.redirect_code or 301
    validate_redirect_code(redirect_code)

    if payload.link_id:
        link_id = normalize_link_id(payload.link_id)
        validate_link_id(link_id)
        if repo.exists(link_id):
            raise HTTPException(
                status_code=409, detail="link_id already taken")
    else:
        # Generate a unique id using the repository exists() check
        link_id = generate_unique_link_id(repo.exists)

    # Create edit token and hash
    edit_token = generate_edit_token()
    edit_token_hash = hash_token(edit_token, pepper=pepper)

    try:
        link = repo.create(
            link_id=link_id,
            target_url=target_url,
            redirect_code=redirect_code,
            edit_token_hash=edit_token_hash,
        )
    except ConflictError as exc:
        # Rare race when id was taken between exists() and create()
        raise HTTPException(
            status_code=409, detail="link_id already taken") from exc

    short_url = f"{base_url.rstrip('/')}/{link.link_id}"
    return CreateLinkResponse(
        link_id=link.link_id,
        short_url=short_url,
        edit_token=edit_token,
        redirect_code=link.redirect_code,
        created_at=link.created_at,
    )


@app.patch("/api/links/{link_id}", response_model=LinkOut)
async def update_link(
    link_id: str,
    payload: UpdateLinkRequest,
    db: Session = Depends(get_db),
    pepper: str | None = Depends(get_token_pepper),
    edit_token: str = Depends(get_edit_token),
) -> LinkOut:
    """Update target_url/redirect_code or optionally change alias; requires edit token.

    Alias change semantics (tombstoning): old alias becomes inactive (returns 410)
    and new alias serves redirects. Token remains the same for MVP (could rotate later).
    """
    repo = LinkRepository(db)

    # fetch link to access stored hash
    try:
        current = repo.get(link_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Link not found") from exc

    if not verify_token(edit_token, current.edit_token_hash, pepper=pepper):
        raise HTTPException(status_code=403, detail="invalid edit token")

    # Apply validations
    new_target = normalize_url(
        payload.target_url) if payload.target_url else None
    new_code = payload.redirect_code
    if new_code is not None:
        validate_redirect_code(new_code)

    # Alias change
    if payload.new_link_id:
        new_alias = normalize_link_id(payload.new_link_id)
        validate_link_id(new_alias)
        if repo.exists(new_alias):
            raise HTTPException(
                status_code=409, detail="new_link_id already taken")
        try:
            updated = repo.change_id(link_id, new_alias)
        except NotFoundError as exc:
            raise HTTPException(
                status_code=404, detail="Link not found") from exc
        link_id = updated.link_id

    # Partial update
    try:
        updated = repo.update(
            link_id,
            target_url=new_target,
            redirect_code=new_code,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Link not found") from exc

    return LinkOut(**asdict(updated))


@app.delete("/api/links/{link_id}")
async def delete_link(
    link_id: str,
    db: Session = Depends(get_db),
    pepper: str | None = Depends(get_token_pepper),
    edit_token: str = Depends(get_edit_token),
) -> dict[str, str]:
    """Soft-delete a link by marking it inactive; requires a valid edit token."""
    repo = LinkRepository(db)
    # Fetch and verify token
    try:
        current = repo.get(link_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Link not found") from exc

    if not verify_token(edit_token, current.edit_token_hash, pepper=pepper):
        raise HTTPException(status_code=403, detail="invalid edit token")

    # Soft-delete
    try:
        link = repo.update(link_id, active=False)
    except NotFoundError as exc:  # should not happen if get succeeded
        raise HTTPException(status_code=404, detail="Link not found") from exc
    return {"status": "deleted", "link_id": link.link_id}
