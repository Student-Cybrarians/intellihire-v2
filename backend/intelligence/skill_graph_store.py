"""Persistent Career Digital Twin skill-graph storage.

The graph is derived only from the deterministic Career Twin output.  It stores
an immutable-ish graph snapshot per user/twin fingerprint and exposes a latest
view for downstream research, roadmap, and readiness services.
"""
import hashlib
import json

from backend.auth.auth_db import db_connect


def _fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _normalize_graph(twin):
    nodes = []
    for item in twin.get("skill_graph") or []:
        skill = str(item.get("skill", "")).strip().lower()
        state = str(item.get("state", "")).strip().lower()
        if not skill or state not in {"evidenced", "gap", "transferable"}:
            continue
        nodes.append({
            "skill": skill,
            "state": state,
            "priority": str(item.get("priority", "medium")),
            "evidence": str(item.get("evidence", ""))[:1000],
        })
    nodes.sort(key=lambda item: (item["skill"], item["state"]))

    required = {str(value).strip().lower() for value in twin.get("required_skills", []) if str(value).strip()}
    edges = []
    role = str(twin.get("role", "")).strip()
    if role:
        for node in nodes:
            relation = "required_for_role" if node["skill"] in required else "transferable_to_role"
            if node["state"] == "gap":
                relation = "required_for_role"
            edges.append({"from": node["skill"], "to": role, "relation": relation})
    edges.sort(key=lambda item: (item["from"], item["relation"], item["to"]))
    return {"version": 1, "role": role, "nodes": nodes, "edges": edges}


def ensure_schema():
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS career_skill_graphs (
                id BIGSERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                twin_fingerprint TEXT NOT NULL,
                graph JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE(user_id, twin_fingerprint)
            )""")
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_career_skill_graphs_user_updated "
                "ON career_skill_graphs(user_id, updated_at DESC)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_career_skill_graphs_graph_gin "
                "ON career_skill_graphs USING GIN(graph jsonb_path_ops)"
            )


def save(user_id, twin, twin_fingerprint=None):
    graph = _normalize_graph(twin)
    fingerprint = twin_fingerprint or _fingerprint({
        "role": twin.get("role", ""),
        "required_skills": sorted(twin.get("required_skills", [])),
        "evidenced_skills": sorted(twin.get("evidenced_skills", [])),
        "skill_graph": graph,
    })
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO career_skill_graphs
                (user_id, twin_fingerprint, graph, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (user_id, twin_fingerprint)
                DO UPDATE SET graph=EXCLUDED.graph, updated_at=NOW()""",
                (user_id, fingerprint, json.dumps(graph, ensure_ascii=False)))
    return {"saved": True, "twin_fingerprint": fingerprint, "graph": graph}


def latest(user_id):
    ensure_schema()
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT graph, twin_fingerprint, updated_at
                           FROM career_skill_graphs
                           WHERE user_id=%s
                           ORDER BY updated_at DESC
                           LIMIT 1""", (user_id,))
            row = cur.fetchone()
    if not row:
        return None
    graph = row[0] if isinstance(row[0], dict) else json.loads(row[0])
    graph["twin_fingerprint"] = row[1]
    graph["updated_at"] = row[2].isoformat() if row[2] else None
    return graph
