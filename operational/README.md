# IntelliHire Operational Boundary

`operational/` is the canonical integration boundary for the production application.

## Rules

- `operational/frontend/` owns browser-side API access and shared frontend contracts.
- `operational/backend/` owns backend integration contracts and deployment-facing notes.
- The existing Next.js `app/` directory remains the Vercel/Next.js runtime entrypoint; it must consume shared contracts from `operational/frontend` rather than inventing API URLs.
- The existing `api/index.py` remains the Vercel WSGI adapter; it connects the deployed `/api/*` boundary to the Flask application.
- Browser requests use same-origin `/api/...` URLs so authentication cookies and API calls stay on the IntelliHire domain.
- Backend providers (AI, auth, persistence and module engines) remain server-side and are never exposed directly to the browser.

## Production flow

Browser UI -> `operational/frontend` API client -> `/api/*` -> `api/index.py` -> Flask backend -> module/AI/store services.

This boundary is deliberately additive: it avoids breaking the current Next.js routing while making the integration contract explicit and testable.
