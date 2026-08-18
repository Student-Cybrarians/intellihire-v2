# Backend Integration Contract

## Public runtime boundary

Vercel invokes `api/index.py` for `/api/*` requests. That adapter imports the Flask application from `backend.core.app`, registers authentication aliases, and applies production hardening.

## Browser contract

The browser must call same-origin endpoints only:

- `GET /api/auth/me` — current authenticated user/session.
- `GET /api/auth/google` — start Google OAuth.
- `GET /api/auth/logout` — terminate session.
- `POST /api/ai/generate` — AI generation/orchestration boundary.
- Module-specific `/api/...` routes — authenticated module operations.

## Security boundary

Provider API keys, database credentials and backend implementation details stay server-side. The frontend receives JSON results only.

## Deployment invariant

Do not point browser code directly at a Python module, provider URL, localhost URL, or deployment-specific hostname. Same-origin `/api/*` paths are the stable production contract.
