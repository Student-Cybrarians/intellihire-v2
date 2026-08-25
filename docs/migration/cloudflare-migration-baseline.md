# IntelliHire Cloudflare Migration Baseline

Date: 2026-08-25
Canonical repository: `Student-Cybrarians/intellihire-v2`
Canonical branch: `master-branch`

## Freeze point

- `master-branch` commit SHA: `fcc3103dae8a07793491330d73e206d8be2f862f`
- Repository tree SHA at freeze: `fcc3103dae8a07793491330d73e206d8be2f862f`
- `package.json` blob SHA: `714c163107934522b42a616a51ad4d402e8d646a`
- `requirements.txt` blob SHA: `764478ccd5d9d83ec37d1b587edff951e6427b47`
- Package lock: **not present in the repository tree**; no lockfile SHA can be recorded.

## Current source topology

The repository contains a Next.js 14 App Router frontend under `app/` and a Flask/Python backend under `backend/`. The root `index.py` imports `backend.core.app` and applies production hardening. `api/index.py` is a thin Vercel adapter around that entrypoint.

The current Vercel configuration is `vercel.json`; it declares the project name `intellihire-v3`, Next.js framework/build settings, a Vercel alias, a Python function for `api/index.py`, and rewrites for `/auth/*` and `/api/*` backend routes.

## Current production/deployment facts verified from GitHub

- Legacy Vercel project named in repository configuration: `intellihire-v3`.
- Legacy production hostname supplied for this migration: `intellihire-v3.vercel.app`.
- Vercel Git deployment is currently encoded in `.github/workflows/vercel-deploy-retry.yml` and `vercel.json`.
- `master-branch` is the Vercel deployment-enabled branch in `vercel.json`.
- Current `master-branch` head was produced by GitHub Actions with message `Record full test diagnostics [skip ci]`.

## Current runtime

- Frontend: Next.js 14.2.x / React 18.
- Backend: Flask 3.1.1 with Gunicorn 23.0.0.
- Database client: psycopg 3.2.9; repository documentation identifies PostgreSQL/Neon as the production database.
- AI providers: OpenAI-compatible and NVIDIA; repository also contains DeepSeek/Tavily configuration expectations.
- Resume/document processing: pypdf, python-docx, openpyxl, reportlab.

## Authentication

Google OAuth is implemented server-side in `backend/auth/oauth_bridge.py` with server-side OAuth state, nonce cookies, ID-token verification, issuer validation, verified-email validation, and PostgreSQL-backed sessions. The current code still contains a hard-coded legacy Vercel canonical host (`intellihire-v2.vercel.app`) and must be normalized to the final Cloudflare production domain before OAuth production cutover.

## Current test state

The latest committed `all-test-report.txt` records **67 passed and 19 failed** tests. Failures include deployment smoke routing, Module 1 AI test imports, Module 4 store imports, research retrieval imports, skill graph store imports, and a Module 5 UI contract assertion. Cloudflare migration must not claim a green baseline until these existing failures are understood and either fixed or explicitly classified.

## Not yet verified

The following require access to the actual deployment/provider control planes or a reachable production endpoint and are intentionally not guessed:

- current Vercel deployment SHA
- current Vercel deployment status/alias metadata
- Vercel environment-variable values
- Google Cloud OAuth configuration currently registered
- active Neon database connection details/status
- custom production domain ownership and DNS zone
- Cloudflare account/zone/Worker project identifiers
- Cloudflare API credentials

## Rollback principle

No Vercel project, deployment, database, authentication configuration, or secret should be deleted during discovery or migration. Vercel remains the rollback host until the Cloudflare production endpoint has passed the complete smoke-test matrix and the final canonical domain has been verified.
