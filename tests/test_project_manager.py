from backend.project_manager import ProjectManager, Task, TaskStatus, TestResult, TestStatus


def test_default_suite_contains_core_gates():
    manager = ProjectManager()
    ids = {case.test_id for case in manager.build_default_test_suite()}
    assert {"build", "typecheck", "lint", "regression", "deployment"} <= ids


def test_pass_moves_to_optimization_and_can_collect_features():
    manager = ProjectManager()
    result = TestResult(
        test_id="regression",
        status=TestStatus.PASS,
        expected_result="all critical regression tests pass",
        actual_result="all tests passed",
        evidence=["pytest output"],
    )
    actions = manager.handle_test_result(
        result,
        research=lambda _: ["add deployment smoke-test coverage"],
    )
    assert manager.state.value == "optimizing"
    assert "research justified improvements" in actions
    assert manager.feature_candidates


def test_fail_enters_repair_loop():
    manager = ProjectManager()
    result = TestResult(
        test_id="deployment",
        status=TestStatus.FAIL,
        expected_result="deployment succeeds and health checks pass",
        actual_result="health endpoint returned 500",
        evidence=["deployment logs"],
        failure_class="deployment",
    )
    actions = manager.handle_test_result(result)
    assert manager.state.value == "repairing"
    assert result.repair_required is True
    assert "identify root cause" in actions


def test_repair_retries_then_blocks():
    manager = ProjectManager()
    manager.add_task(Task(task_id="T1", objective="repair API"))
    task = manager.tasks["T1"]
    task.max_retries = 1
    manager.repair_task("T1", "bad configuration")
    task.status = TaskStatus.TESTING
    manager.repair_task("T1", "bad configuration")
    assert manager.tasks["T1"].status is TaskStatus.BLOCKED
    assert manager.state.value == "blocked"


def test_production_verification_failure_returns_to_repair():
    manager = ProjectManager()
    manager.verify_production(False, ["/health returned 500"])
    assert manager.state.value == "repairing"


def test_production_verification_success_completes():
    manager = ProjectManager()
    manager.verify_production(True, ["/health 200", "login smoke test passed"])
    assert manager.state.value == "complete"
