# IntelliHire Production Repair — Phase 0 Baseline

Date: 2026-08-16

## Goal
Establish the route, action, backend, AI, and deployment inventory before making functional repairs.

## Current application surfaces

### Public Next.js pages
- `/`
- `/features`
- `/courses`
- `/pricing`
- `/about`
- `/contact`
- `/faq`

### Authentication
- `/signin`
- `/signup` / registration flow where present
- `/auth/google`
- logout/session paths

### Application surfaces
- dashboard
- module 1
- module 2
- module 3
- module 4
- module 5
- career intelligence / roadmap surfaces
- admin

### Backend/AI surfaces
- `app/api/ai/generate/route.ts`
- `api/index.py`
- Flask application and route modules
- `ai/context.py`
- `ai/orchestrator.py`
- `ai/providers.py`
- `ai/schemas.py`
- module-specific AI engines
- research/context/retrieval components

## Deployment
- Production branch: `master-branch`
- Vercel project: `intellihire-v2`
- Automatic deployments: master only; feature branches disabled
- Known external blocker: Vercel deployment quota may prevent immediate production deployment

## Repair phases
1. Baseline/inventory
2. Public website
3. Authentication
4. Dashboard/navigation
5. Modules 1–5
6. AI/DeepSeek
7. Admin
8. Backend/API
9. Responsive UX
10. SEO/LLM/accessibility
11. Performance
12. Security + production validation

## Phase 0 exit criteria
- [x] Repository architecture inspected
- [x] Public page surface identified
- [x] AI/backend surface identified
- [x] Vercel deployment constraints recorded
- [ ] Every route enumerated from source
- [ ] Every interactive action enumerated from source
- [ ] Existing test/CI results reviewed
- [ ] Broken-route/action candidates classified

## Safety rule
Do not delete legacy Flask/template files until their runtime ownership is verified. Do not replace module-specific logic with generic placeholders.
