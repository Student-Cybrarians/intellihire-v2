#!/usr/bin/env bash
set -euo pipefail

ROOT="$PWD"
mkdir -p backend/api backend/core backend/auth backend/intelligence backend/modules/module1 backend/modules/module2 backend/modules/module3 backend/modules/module4 backend/modules/module5 backend/research

# The backend folders currently contain migration wrappers. Remove those wrappers
# so the existing, tested implementations can be moved into their canonical homes.
for d in backend/ai backend/auth backend/core backend/intelligence backend/modules backend/research; do
  # Keep the top-level backend package itself; its children are rebuilt below.
  if [[ -d "$d" ]]; then
    find "$d" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  fi
done

# Move the existing AI implementation into the backend boundary.
if [[ -d ai ]]; then git mv ai backend/ai; fi

move_if_present() {
  local src="$1" dst="$2"
  if [[ -f "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    git mv "$src" "$dst"
  fi
}

move_if_present app.py backend/core/app.py
move_if_present production_hardening.py backend/core/production_hardening.py
move_if_present ai_routes.py backend/api/ai_routes.py
move_if_present auth_api_alias.py backend/api/auth_api_alias.py
move_if_present auth_db.py backend/auth/auth_db.py
move_if_present auth_routes.py backend/auth/auth_routes.py
move_if_present public_routes.py backend/auth/public_routes.py
move_if_present career_intelligence.py backend/intelligence/career_intelligence.py
move_if_present career_twin_store.py backend/intelligence/career_twin_store.py
move_if_present ml_engine.py backend/intelligence/ml_engine.py
move_if_present readiness_store.py backend/intelligence/readiness_store.py
move_if_present roadmap_engine.py backend/intelligence/roadmap_engine.py
move_if_present roadmap_store.py backend/intelligence/roadmap_store.py
move_if_present skill_graph_store.py backend/intelligence/skill_graph_store.py
move_if_present module1_ai.py backend/modules/module1/module1_ai.py
move_if_present module2_engine.py backend/modules/module2/module2_engine.py
move_if_present module2_routes.py backend/modules/module2/module2_routes.py
move_if_present module2_store.py backend/modules/module2/module2_store.py
move_if_present module3_adaptive.py backend/modules/module3/module3_adaptive.py
move_if_present module3_evaluator.py backend/modules/module3/module3_evaluator.py
move_if_present module3_routes.py backend/modules/module3/module3_routes.py
move_if_present module3_store.py backend/modules/module3/module3_store.py
move_if_present module4_competency.py backend/modules/module4/module4_competency.py
move_if_present module4_competency_store.py backend/modules/module4/module4_competency_store.py
move_if_present module4_hr.py backend/modules/module4/module4_hr.py
move_if_present module4_liftoff.py backend/modules/module4/module4_liftoff.py
move_if_present module4_routes.py backend/modules/module4/module4_routes.py
move_if_present module4_store.py backend/modules/module4/module4_store.py
move_if_present module5_engine.py backend/modules/module5/module5_engine.py
move_if_present module5_readiness.py backend/modules/module5/module5_readiness.py
move_if_present module5_routes.py backend/modules/module5/module5_routes.py
move_if_present research_context.py backend/research/research_context.py
move_if_present research_engine.py backend/research/research_engine.py
move_if_present research_retrieval.py backend/research/research_retrieval.py
move_if_present research_store.py backend/research/research_store.py

# Make every backend directory a real Python package.
touch backend/api/__init__.py backend/core/__init__.py backend/auth/__init__.py backend/intelligence/__init__.py backend/modules/__init__.py backend/modules/module1/__init__.py backend/modules/module2/__init__.py backend/modules/module3/__init__.py backend/modules/module4/__init__.py backend/modules/module5/__init__.py backend/research/__init__.py

# Rewrite Python imports from the former root-level module names to their
# canonical backend packages. This is deliberately mechanical so behavior is unchanged.
python - <<'PY'
from pathlib import Path

mapping = {
    'ai': 'backend.ai',
    'ai_routes': 'backend.api.ai_routes',
    'auth_api_alias': 'backend.api.auth_api_alias',
    'auth_db': 'backend.auth.auth_db',
    'auth_routes': 'backend.auth.auth_routes',
    'public_routes': 'backend.auth.public_routes',
    'career_intelligence': 'backend.intelligence.career_intelligence',
    'career_twin_store': 'backend.intelligence.career_twin_store',
    'ml_engine': 'backend.intelligence.ml_engine',
    'readiness_store': 'backend.intelligence.readiness_store',
    'roadmap_engine': 'backend.intelligence.roadmap_engine',
    'roadmap_store': 'backend.intelligence.roadmap_store',
    'skill_graph_store': 'backend.intelligence.skill_graph_store',
    'module1_ai': 'backend.modules.module1.module1_ai',
    'module2_engine': 'backend.modules.module2.module2_engine',
    'module2_routes': 'backend.modules.module2.module2_routes',
    'module2_store': 'backend.modules.module2.module2_store',
    'module3_adaptive': 'backend.modules.module3.module3_adaptive',
    'module3_evaluator': 'backend.modules.module3.module3_evaluator',
    'module3_routes': 'backend.modules.module3.module3_routes',
    'module3_store': 'backend.modules.module3.module3_store',
    'module4_competency': 'backend.modules.module4.module4_competency',
    'module4_competency_store': 'backend.modules.module4.module4_competency_store',
    'module4_hr': 'backend.modules.module4.module4_hr',
    'module4_liftoff': 'backend.modules.module4.module4_liftoff',
    'module4_routes': 'backend.modules.module4.module4_routes',
    'module4_store': 'backend.modules.module4.module4_store',
    'module5_engine': 'backend.modules.module5.module5_engine',
    'module5_readiness': 'backend.modules.module5.module5_readiness',
    'module5_routes': 'backend.modules.module5.module5_routes',
    'research_context': 'backend.research.research_context',
    'research_engine': 'backend.research.research_engine',
    'research_retrieval': 'backend.research.research_retrieval',
    'research_store': 'backend.research.research_store',
}

files = list(Path('.').rglob('*.py'))
for path in files:
    if any(part in {'.git', '.next', 'node_modules'} for part in path.parts):
        continue
    text = path.read_text(encoding='utf-8')
    original = text
    for old, new in sorted(mapping.items(), key=lambda x: -len(x[0])):
        text = text.replace(f'from {old} import', f'from {new} import')
        text = text.replace(f'import {old}', f'import {new}')
    if text != original:
        path.write_text(text, encoding='utf-8')
PY

# Canonical root WSGI entrypoint. Vercel still reaches it through api/index.py.
cat > index.py <<'PY'
"""Canonical IntelliHire backend entrypoint.

The repository root intentionally contains only this Python entrypoint. All
application implementation lives under backend/.
"""
from backend.core.app import app
from backend.core.production_hardening import install
from backend.api.auth_api_alias import auth_api

if "auth_api" not in app.blueprints:
    app.register_blueprint(auth_api)

install(app)
handler = app
PY

# Vercel's /api boundary remains a thin adapter to the canonical root entrypoint.
cat > api/index.py <<'PY'
"""Thin Vercel adapter for the canonical IntelliHire backend entrypoint."""
from index import app, handler

__all__ = ["app", "handler"]
PY

# pytest must resolve the new backend package paths during CI.
cat > pytest.ini <<'EOF'
[pytest]
pythonpath = .
EOF

# Keep the repository architecture documentation synchronized with the actual tree.
cat > docs/architecture/repository-architecture.md <<'EOF'
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
EOF

# Remove the one-shot migration files after this commit; the resulting tree should
# contain only normal project automation under .github.
git rm -f .github/scripts/reorganize_backend.sh .github/workflows/reorganize-backend.yml 2>/dev/null || true
