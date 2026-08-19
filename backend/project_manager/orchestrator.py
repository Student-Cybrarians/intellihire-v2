"""Deterministic orchestration engine for IntelliHire project execution.

The module deliberately contains no provider-specific AI client.  An AI/LLM layer can
use these state transitions and policies while keeping execution auditable and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from .models import ProjectState, Task, TaskStatus, TestCase, TestResult, TestStatus


@dataclass(slots=True)
class ProjectManagerConfig:
    max_repair_cycles: int = 3
    critical_severities: set[str] = field(
        default_factory=lambda: {"critical", "high"}
    )
    require_production_verification: bool = True


@dataclass(slots=True)
class ProjectManager:
    """State machine implementing the project lifecycle and repair loop."""

    config: ProjectManagerConfig = field(default_factory=ProjectManagerConfig)
    state: ProjectState = ProjectState.DISCOVERING
    tasks: dict[str, Task] = field(default_factory=dict)
    test_results: dict[str, TestResult] = field(default_factory=dict)
    events: list[dict[str, str]] = field(default_factory=list)
    feature_candidates: list[dict[str, str]] = field(default_factory=list)

    def emit(self, event: str, detail: str = "") -> None:
        self.events.append({"event": event, "detail": detail})

    def transition(self, new_state: ProjectState) -> None:
        self.emit("state_transition", f"{self.state.value} -> {new_state.value}")
        self.state = new_state

    def add_task(self, task: Task) -> Task:
        if task.task_id in self.tasks:
            raise ValueError(f"duplicate task id: {task.task_id}")
        self.tasks[task.task_id] = task
        self.emit("task_created", task.task_id)
        return task

    def advance_task(self, task_id: str, status: TaskStatus, evidence: Iterable[str] = ()) -> Task:
        task = self.tasks[task_id]
        task.status = status
        task.evidence.extend(evidence)
        task.touch()
        self.emit("task_status", f"{task_id}:{status.value}")
        return task

    def build_default_test_suite(self) -> list[TestCase]:
        return [
            TestCase(
                "build",
                "Production build",
                "Build completes without error",
                ["record build artifact", "continue to verification"],
                ["capture build log", "classify root cause", "repair and rebuild"],
                "production build succeeds",
                severity="critical",
                automated_command="npm run build",
            ),
            TestCase(
                "typecheck",
                "Static type validation",
                "TypeScript reports no type errors",
                ["record clean typecheck"],
                ["repair type errors", "rerun typecheck", "run regression tests"],
                "tsc exits 0",
                severity="high",
                automated_command="npm run typecheck",
            ),
            TestCase(
                "lint",
                "Code quality validation",
                "Lint completes without blocking errors",
                ["record clean lint"],
                ["repair lint violations", "rerun lint"],
                "lint exits 0",
                severity="medium",
                automated_command="npm run lint",
            ),
            TestCase(
                "regression",
                "Critical regression suite",
                "Existing IntelliHire regression tests pass",
                ["mark milestone verified", "research improvements"],
                ["freeze feature work", "reproduce failure", "repair", "rerun regression"],
                "all critical regression tests pass",
                severity="critical",
                automated_command="pytest -q",
            ),
            TestCase(
                "deployment",
                "Production deployment",
                "Deployment completes and production routes respond",
                ["run smoke tests", "record deployment evidence"],
                ["inspect deployment logs", "repair or rollback", "redeploy"],
                "deployment succeeds and health checks pass",
                severity="critical",
            ),
        ]

    def record_test(self, result: TestResult) -> TestResult:
        self.test_results[result.test_id] = result
        self.emit("test_result", f"{result.test_id}:{result.status.value}")
        if result.status is TestStatus.FAIL:
            result.repair_required = True
        return result

    def handle_test_result(
        self,
        result: TestResult,
        research: Callable[[TestResult], list[str]] | None = None,
    ) -> list[str]:
        """Apply pass/fail policy and return immediate next actions."""
        self.record_test(result)

        if result.status is TestStatus.PASS:
            actions = [
                "verify acceptance criteria",
                "record evidence",
                "check regression impact",
                "research justified improvements",
                "prioritize next features",
            ]
            if research:
                recommendations = research(result)
                result.recommendations.extend(recommendations)
                self.feature_candidates.extend(
                    {"test_id": result.test_id, "recommendation": item}
                    for item in recommendations
                )
            self.transition(ProjectState.OPTIMIZING)
            return actions

        if result.status is TestStatus.BLOCKED:
            self.transition(ProjectState.BLOCKED)
            return ["capture blocker", "escalate external dependency or human decision"]

        self.transition(ProjectState.REPAIRING)
        return [
            "freeze feature expansion for affected component",
            "reproduce failure",
            "classify failure",
            "identify root cause",
            "research repair options",
            "create repair plan",
            "implement repair",
            "rerun affected test",
            "run regression tests",
        ]

    def repair_task(self, task_id: str, root_cause: str) -> Task:
        task = self.tasks[task_id]
        if task.retry_count >= min(task.max_retries, self.config.max_repair_cycles):
            task.status = TaskStatus.BLOCKED
            task.notes.append("repair retry limit reached")
            self.transition(ProjectState.BLOCKED)
            return task
        task.retry_count += 1
        task.status = TaskStatus.REPAIRING
        task.notes.append(f"repair cycle {task.retry_count}: {root_cause}")
        task.touch()
        self.emit("repair_cycle", f"{task_id}:{task.retry_count}")
        return task

    def ready_for_deployment(self) -> bool:
        blocking_tests = [
            result
            for result in self.test_results.values()
            if result.status is not TestStatus.PASS
            and result.test_id in {"build", "typecheck", "regression"}
        ]
        return not blocking_tests

    def verify_production(self, checks_passed: bool, evidence: Iterable[str] = ()) -> None:
        if checks_passed:
            self.emit("production_verified", "; ".join(evidence))
            self.transition(ProjectState.COMPLETE)
            return
        self.emit("production_failed", "; ".join(evidence))
        self.transition(ProjectState.REPAIRING)

    def summary(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "tasks": {key: value.to_dict() for key, value in self.tasks.items()},
            "tests": {
                key: value.to_dict() for key, value in self.test_results.items()
            },
            "feature_candidates": self.feature_candidates,
            "events": self.events,
        }
