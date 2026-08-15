import json

import skill_graph_store


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.row

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConn:
    def __init__(self, cursor):
        self.cursor_obj = cursor

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def sample_twin():
    return {
        "role": "Software Engineer",
        "required_skills": ["python", "docker"],
        "evidenced_skills": ["python", "git"],
        "skill_graph": [
            {"skill": "python", "state": "evidenced", "priority": "maintain", "evidence": "Built APIs with Python"},
            {"skill": "docker", "state": "gap", "priority": "high", "evidence": ""},
            {"skill": "git", "state": "transferable", "priority": "medium", "evidence": "Used Git daily"},
        ],
    }


def test_normalize_graph_preserves_evidence_boundary():
    graph = skill_graph_store._normalize_graph(sample_twin())
    assert graph["version"] == 1
    assert {node["skill"] for node in graph["nodes"]} == {"python", "docker", "git"}
    assert next(node for node in graph["nodes"] if node["skill"] == "docker")["evidence"] == ""
    assert any(edge["from"] == "docker" and edge["relation"] == "required_for_role" for edge in graph["edges"])
    assert any(edge["from"] == "git" and edge["relation"] == "transferable_to_role" for edge in graph["edges"])


def test_save_uses_upsert_and_jsonb(monkeypatch):
    cursor = FakeCursor()
    conn = FakeConn(cursor)
    monkeypatch.setattr(skill_graph_store, "db_connect", lambda: conn)
    result = skill_graph_store.save("00000000-0000-0000-0000-000000000001", sample_twin())
    assert result["saved"] is True
    assert result["graph"]["role"] == "Software Engineer"
    insert_calls = [call for call in cursor.calls if "INSERT INTO career_skill_graphs" in call[0]]
    assert len(insert_calls) == 1
    assert json.loads(insert_calls[0][1][2])["version"] == 1


def test_latest_is_user_scoped_and_round_trips_json(monkeypatch):
    graph = {"version": 1, "role": "Backend Engineer", "nodes": [], "edges": []}
    cursor = FakeCursor((json.dumps(graph), "fingerprint", None))
    conn = FakeConn(cursor)
    monkeypatch.setattr(skill_graph_store, "db_connect", lambda: conn)
    result = skill_graph_store.latest("00000000-0000-0000-0000-000000000001")
    assert result["role"] == "Backend Engineer"
    assert result["twin_fingerprint"] == "fingerprint"
    select = [call for call in cursor.calls if "FROM career_skill_graphs" in call[0]][0]
    assert select[1] == ("00000000-0000-0000-0000-000000000001",)
