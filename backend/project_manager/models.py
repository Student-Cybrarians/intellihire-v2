"""Typed state models for the IntelliHire project-management loop."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    RESEARCHING = "researching"
    PLANNED = "planned"
    DESIGNING = "designing"
    READY = "ready"
    BUILDING = "building"
    TESTING = "testing"
    REPAIRING = "repairing"
    PASSED = "passed"
    DEPLOYING = "deploying"
    VERIFIED = "verified"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ROLLBACK = "rollback"


class TestStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NOT_RUN = "not_run"


class ProjectState(str, Enum):
    DISCOVERING = "discovering"
    RESEARCHING = "researching"
    PLANNING = "planning"
    DESIGNING = "designing"
    BUILDING = "building"
    TESTING = "testing"
    REPAIRING = "repairing"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    OPTIMIZING = "optimizing"
    BLOCKED = "blocked"
    COMPLETE = "complete"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Task:
    task_id: str
    objective: str
    status: TaskStatus = TaskStatus.BACKLOG
    owner: str = "project-manager"
    dependencies: list[str] = field(default_factory=list)
    affected_paths: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    validation: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(slots=True)
class TestCase:
    test_id: str
    name: str
    condition: str
    action_on_pass: list[str]
    action_on_fail: list[str]
    expected_result: str
    severity: str = "medium"
    automated_command: str | None = None


@dataclass(slots=True)
class TestResult:
    test_id: str
    status: TestStatus
    expected_result: str
    actual_result: str
    evidence: list[str] = field(default_factory=list)
    failure_class: str | None = None
    root_cause: str | None = None
    repair_required: bool = False
    recommendations: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload
