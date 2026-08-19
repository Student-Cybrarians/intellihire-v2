# IntelliHire Project Manager

The Project Manager is a deterministic orchestration boundary for planning, research, design, development, testing, deployment, repair, and optimization.

## Lifecycle

```text
DISCOVER
  -> RESEARCH
  -> PLAN
  -> DESIGN
  -> BUILD
  -> TEST
  -> DEPLOY
  -> VERIFY
  -> OPTIMIZE
  -> NEXT ITERATION
```

Failure uses a closed repair loop:

```text
FAIL
  -> REPRODUCE
  -> ROOT CAUSE
  -> RESEARCH
  -> REPLAN
  -> REDESIGN
  -> REPAIR
  -> RETEST
  -> REGRESSION
  -> DEPLOY
  -> VERIFY
```

Passing a test causes the manager to record evidence and research justified next features. A pass does not automatically authorize scope expansion. A failure blocks feature expansion for the affected component until repair and regression verification complete.

## Integration contract

The package is intentionally provider-neutral. An LLM/agent runtime can call `ProjectManager` to manage state and use `roles.py` to construct specialist prompts. This avoids coupling the business workflow to a single AI provider.

Example:

```python
from backend.project_manager import ProjectManager, TestResult, TestStatus

manager = ProjectManager()
for case in manager.build_default_test_suite():
    print(case.test_id, case.automated_command)

manager.handle_test_result(
    TestResult(
        test_id="build",
        status=TestStatus.PASS,
        expected_result="production build succeeds",
        actual_result="build completed",
        evidence=["CI build log"],
    )
)
```

## Safety

The manager does not execute shell commands or mutate production by itself. Execution should be performed by the repository's existing CI/CD and agent runtime, with production-sensitive operations gated by the deployment agent/human approval policy.
