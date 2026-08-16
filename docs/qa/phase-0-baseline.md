# Phase 0 — Baseline & Route/Action Inventory

Date: 2026-08-16

## Current architecture

- Next.js 14 App Router frontend under `app/`.
- Python/Flask compatibility/backend surface remains at repository root and under `api/`.
- Shared AI layer exists under `ai/` with context, orchestrator, providers, and schemas.
- Vercel entrypoint is `api/index.py`.
- Public marketing routes include `/`, `/about`, `/features`, `/courses`, `/pricing`, `/faq`, and `/contact`.
- Authentication surface exists under `app/auth/` and legacy Python auth routes also exist.
- A nested `app/app/module3/...` route exists and requires verification because the duplicated `app` segment is easy to misroute.

## Immediate findings

1. `app/marketing/MarketingShell.tsx` has a contact form that only changes local state to `Message ready ✓`; it does not submit to a backend endpoint. Phase 1 must either wire a real endpoint or clearly implement a local success flow without implying delivery.
2. The back-to-top control uses `href="#"`; replace with a semantic button/scroll action or `href="#top"` with a matching anchor.
3. The homepage's primary CTA points to `/auth/google`; verify that Google authentication is configured and that this route is the intended onboarding path.
4. Public navigation is generated from fixed paths; verify each target exists and each page has correct active state.
5. The repository contains both Next.js and legacy Flask/template surfaces. Do not delete legacy code until runtime ownership is proven.
6. Vercel deployment is constrained by the previously observed deployment quota; production verification must be treated as an external blocker until the quota clears.

## Phase gates

- Phase 0: inventory complete when all route families, entrypoints, APIs, auth boundaries, and known dead controls are documented.
- Phase 1: public-page and CTA repair.
- Phase 2: authentication repair.
- Phase 3: dashboard/navigation repair.
- Phase 4: Modules 1–5 end-to-end repair.
- Phase 5: AI/DeepSeek reliability.
- Phase 6: admin repair.
- Phase 7: backend/API contracts.
- Phase 8: responsive UX.
- Phase 9: SEO/LLM/accessibility verification.
- Phase 10: performance.
- Phase 11: security.
- Phase 12: production smoke test.

## Phase 0 exit status

**Inventory complete enough to begin Phase 1.** No destructive cleanup is approved yet.
