# IntelliHire Repository Architecture

## Target structure

```text
intellihire-v2/
├── index.py                    # only root-level Python application entrypoint
├── app/                        # Next.js frontend routes/components
├── backend/
│   ├── api/                    # Flask/Vercel API adapters
│   ├── core/                   # Flask application + production hardening
│   ├── ai/                     # shared AI orchestration/providers/schemas
│   ├── auth/                   # authentication, persistence, public routes
│   ├── intelligence/           # career intelligence, roadmap, skill graph
│   ├── modules/module1..5/     # module-specific engines, stores, routes
│   └── research/               # research context/retrieval/store/engine
├── api/index.py                # thin Vercel /api adapter only
├── templates/                  # legacy Flask presentation
├── static/                     # legacy Flask assets
├── tests/                      # regression/integration/contract tests
├── scripts/                    # maintenance utilities
├── prompts/                    # versioned AI prompts
└── .github/workflows/          # CI/CD
```

## Runtime connection

`app/` is the Next.js presentation layer. Browser requests use same-origin `/api/*` routes. Vercel routes `/api/index.py` to the Flask application, which is imported from the canonical root `index.py` and implemented under `backend/`. Secrets and provider calls remain server-side.

## Migration rule

No backend implementation belongs at repository root. The root Python surface is intentionally limited to `index.py`; frontend configuration files such as `package.json`, `next.config.mjs`, `tsconfig.json`, and `vercel.json` remain at root because Next.js/Vercel require them there.
