# TinyURL requirements

Here is a set of functional and non-functional requirements for a TinyURL-type application (URL shortener).

---

## Functional requirements

### Adding a new link

1. The user can submit an original URL to shorten.
2. If no `link-id` is provided, the system generates one as 6 hexadecimal characters `[0-9a-f]` (lowercase).
   - The system must ensure uniqueness atomically; on collision, retry generation (up to 5 attempts, then 500).
3. The user may optionally provide a custom `link-id` (e.g., `my-link`) subject to:
   - Allowed charset: `^[A-Za-z0-9_-]{1,32}$`
   - Normalization: lowercase
   - Not in reserved list: `api`, `admin`, `robots`, `favicon`, `health`, `metrics`, `static`, etc.
4. The user can optionally choose the redirect status code (allowed: 301, 302, 307, 308). Default: 301.
5. The system returns:
   - The shortened URL: `https://tinyurl.domain.com/<link-id>`
   - A high-entropy edit token (see Security) for future edits/deletion.
6. URL validation:
   - Scheme: `http://` or `https://`
   - Max length: 2048 chars
   - Punycode normalization for internationalized domains
   - Disallow private-link schemes (e.g., `file:`, `javascript:`).

### Updating an existing link

1. The user can update:
   - The `target_url`
   - The `redirect_code`
   - Or the `link-id` (alias change)
2. Updates require prividing valid `edit_token`.
3. If changing the `link-id`, the new ID must be unused. By default, the old ID stops working and will return 410 Gone (see Deletion).

### Deleting an existing link

1. The user can request deletion of a previously created link using valid `edit_token`.
2. The system marks the entry as deleted (`active=false`, `target_url` may be nulled). Redirect service must return 410 Gone for that `link-id`.

### Redirection

1. Visiting `https://tinyurl.domain.com/<link-id>` returns a redirect to the original URL with the configured code (301, 302, 307, or 308).
2. For a deleted `link-id`, return 410 Gone. For non-existent IDs, return 404.
3. Support GET and HEAD methods.
4. Caching:
   - 301/308 may include long max-age (configurable).
   - 302/307 should be non-cacheable by default.

## Non-functional requirements

### Performance

1. Handle 1000 redirect requests per second; 95% processed within 100ms, 99% within 300ms (cache hit).
2. O(1) `link-id` → URL lookup via in-memory/Redis cache backed by a persistent store.

### Scalability

1. Enable horizontal scaling.
2. Separate write path (create/update/delete) from read path (redirects).
3. Eventual consistency from write to cache is acceptable (<5s).

### Security

1. Link creation is public but rate-limited (e.g., 100/min/IP for create/update; reasonable limits for delete).
2. Each created link returns an edit token:
   - 24-character random string from `[A-Za-z0-9]` (≈143 bits entropy).
   - Store only a SHA-256 hash (optionally with a server-side pepper); never store plaintext.
   - Optionally rotate token on successful update.
3. UI/API available only over HTTPS. Redirects may be served over HTTP and HTTPS (configurable).
4. CSRF protection on form endpoints; CORS configured if exposing APIs to browsers.
5. Abuse controls: domain blocklist, optional safe-browsing checks, and IP/User-Agent rate limiting.
6. Input validation and output encoding in UI to prevent XSS.

### SEO and redirects

1. Support for 301, 302, 307, and 308:
   - 301 Moved Permanently: cacheable by default; search engines transfer ranking.
   - 302 Found: temporary; not cacheable by default; method may change on some clients.
   - 307 Temporary Redirect: temporary; method preserved.
   - 308 Permanent Redirect: permanent; method preserved; cacheable by default.
2. Serve a static `robots.txt` (configurable).

### Error handling

- 400 Invalid input (e.g., bad URL, bad `link-id` format)
- 401/403 Invalid or missing edit token
- 404 Not found
- 409 Conflict (custom `link-id` already taken)
- 410 Gone (deleted link)
- 429 Too Many Requests (rate limiting)
- 500/503 Server errors

## Data model

Example JSON document representing one entry:

```json
{
  "link_id": "aZ8kL2",
  "target_url": "https://example.com/abc/xyz",
  "redirect_code": 302,
  "created_at": "2025-06-29T14:35:00Z",
  "updated_at": "2025-06-29T14:35:00Z",
  "edit_token_hash": "sha256-hash-of-edit-token",
  "active": true,
  "expires_at": null
}
```

## Logical architecture (Mermaid)

```mermaid
graph TD
  U[User/Browser] --> FE[Frontend / UI]
  FE --> API[API Gateway / Backend API]
  API --> URL[URL Service (write path)]
  API --> REDIR[Redirect Service (read path)]
  URL --> DB[(Persistent DB)]
  REDIR --> CACHE[(In-memory Cache)]
  CACHE --> DB
```

### Components

- API Gateway / Backend API: Entry point; validation; routes write/read traffic.
- Frontend / UI: Forms to add, edit, and browse links.
- URL Service: ID generation; writes/updates/deletes; cache invalidation.
- Redirect Service: High-performance lookups; serves redirects from cache.
- Cache: In-memory/Redis for hot lookups.
- DB: Persistent store (e.g., SQLite for dev; PostgreSQL for prod).

## Technology suggestions

- Frontend: Svelte, Vue, or Preact
- API/Backend: Python (FastAPI)
- API Gateway: Nginx
- Cache: Redis
- Database: SQLite (dev/small) or PostgreSQL (prod)
