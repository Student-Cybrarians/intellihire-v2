# IntelliHire Repository Architecture

## Purpose

This document defines the target repository organization for IntelliHire. The architecture separates the Next.js presentation layer from the Python backend, AI orchestration, domain intelligence, module engines, research services, tests, prompts, deployment automation, and documentation.

## Target structure

```text
intellihire-v2/
├── app/                         # Next.js frontend and route handlers
├── backend/                     # Python backend and intelligence services
│   ├── api/
│   ├── core/
│   ├── ai/
│   ├── auth/
│   ├── intelligence/
│   ├── modules/
│   └── research/
├── prompts/                     # Versioned AI prompts by domain/module
├── tests/                       # Unit, integration, and contract tests
├── scripts/                     # Maintenance and migration utilities
├── docs/                        # Architecture, deployment, development docs
├── public/                      # Frontend static assets
├── .github/workflows/           # CI/CD automation
├── README.md
├── package.json
├── requirements.txt
├── next.config.mjs
├── tsconfig.json
├── vercel.json
└── .env.example
```

## Architectural boundaries

### Frontend

`app/` owns user-facing pages, client components, styling, and Next.js API route handlers. It should not contain Python business logic or provider secrets.

### Backend

`backend/` owns authentication, domain services, module engines, persistence adapters, research, and the AI intelligence layer.

### AI orchestration

`backend/ai/` is the common response/orchestration boundary. Modules may supply module-specific context and schemas, but provider selection, timeout/fallback behavior, structured response validation, and cross-module intelligence remain centralized.

### Prompts

`prompts/` contains versioned prompt assets. Prompt files are configuration/data, not Python application modules.

### Tests

`tests/` mirrors the backend domains and contains regression, integration, deployment, and UI-contract coverage.

## Migration principle

The repository refactor must be performed without changing product behavior. Import paths, Vercel entry points, workflow references, and tests must be migrated together. Legacy Flask templates/static assets should remain only until the corresponding Next.js implementation is verified; they should not be deleted as part of a blind directory move.

## Current-to-target mapping

| Current path | Target responsibility |
|---|---|
| `ai/*` | `backend/ai/*` |
| `app.py` | `backend/core/app.py` |
| `auth_db.py` | `backend/auth/auth_db.py` |
| `auth_routes.py` | `backend/auth/auth_routes.py` |
| `public_routes.py` | `backend/auth/public_routes.py` |
| `career_intelligence.py` | `backend/intelligence/career_intelligence.py` |
| `career_twin_store.py` | `backend/intelligence/career_twin_store.py` |
| `ml_engine.py` | `backend/intelligence/ml_engine.py` |
| `roadmap_*` | `backend/intelligence/` |
| `skill_graph_store.py` | `backend/intelligence/skill_graph_store.py` |
| `module1_ai.py` | `backend/modules/module1/` |
| `module2_*` | `backend/modules/module2/` |
| `module3_*` | `backend/modules/module3/` |
| `module4_*` | `backend/modules/module4/` |
| `module5_*` | `backend/modules/module5/` |
| `research_*` | `backend/research/` |
| `production_hardening.py` | `backend/core/production_hardening.py` |
| `templates/*` | legacy Flask presentation; migrate before removal |
| `static/*` | legacy Flask assets; migrate before removal |
