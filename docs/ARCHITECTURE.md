# Architecture v5.0.0

Browser → `frontend/` → FastAPI `backend/` → `core/` services → platform adapters / artifact output.

## Layer

### frontend
HTML, vanilla JavaScript, CSS responsive, authentication UI, settings, scraper controls, repository view, and PWA.

### backend
HTTP routes, request validation, sessions, gateway, repository catalog, scraper API, asset API, and static frontend serving.

### core
Reusable domain logic without page rendering.

### platforms
Thin adapters grouped by target platform.

### tooling
CLI tools and validation commands.

### tests
Automated regression coverage.

### artifacts
Runtime generated exports and download outputs.

## Gateway

The backend owns `/api` routes. Static frontend assets are mounted once at `/` after API registration, preventing static files from shadowing API endpoints.

## Authentication

Local authentication uses SQLite-backed sessions and PBKDF2 password hashing. Google Login uses OIDC through Authlib when credentials are configured.

## Scraper

The scraper is public-resource oriented. It validates public DNS/IP targets, limits response size, checks robots.txt when available, rejects credential-in-URL targets, and keeps crawl requests on the same host.
