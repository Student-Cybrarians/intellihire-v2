# Phase 3 — Dashboard and application navigation

## Scope
- Add a production Next.js authenticated application dashboard.
- Provide a consistent application navigation model for Modules 1–5.
- Surface the five connected stages without replacing module implementations.
- Keep authentication delegated to the Phase 2 backend session boundary.

## Route contract
- `/app/dashboard` — authenticated dashboard
- `/app/module1` — Module 1 landing surface
- `/app/module2` — Module 2 landing surface
- `/app/module3` — existing technical interview flow
- `/app/module4` — Module 4 landing surface
- `/app/module5` — Module 5 landing surface

## Safety
The dashboard does not invent scores or employment decisions. Module 1/2/4/5 landing surfaces are navigation placeholders until their dedicated implementation phases replace them.
