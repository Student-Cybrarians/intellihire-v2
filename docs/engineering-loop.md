# IntelliHire Engineering Loop

## Purpose

IntelliHire uses a small-change, evidence-driven engineering loop for feature work, repair work, and deployment changes. The loop operationalizes the project guideline: understand the system before changing it, make the smallest correct change, validate it, and repeat only when evidence requires it.

## Loop

```text
OBSERVE
  ↓
BASELINE
  ↓
PLAN
  ↓
IMPLEMENT
  ↓
VERIFY
  ↓
DECIDE
  ├─ PASS → REVIEW → SHIP
  └─ FAIL → ISOLATE → REPAIR → VERIFY
```

### 1. Observe

- Read the relevant source, configuration, tests, and architecture notes.
- Trace the real execution path before editing it.
- Identify existing behavior and constraints.
- Do not redesign unrelated code.

### 2. Baseline

Record the current state before the change:

- frontend typecheck/build
- backend syntax/compile
- targeted regression tests
- relevant deployment/smoke checks
- current runtime assumptions

A failure that already exists is a baseline finding, not automatically a regression caused by the change.

### 3. Plan

Define the smallest change that can satisfy the requested behavior.

- Reuse existing services/components.
- Preserve public contracts unless a contract change is required.
- Add a dependency only when an existing dependency cannot solve the problem.
- Define happy, error, empty, unauthorized, timeout, and recovery behavior when applicable.

### 4. Implement

Change only the files required by the plan.

- Keep business logic in the existing domain boundary.
- Keep secrets server-side.
- Keep AI provider failures explicit.
- Never turn a deterministic fallback into a fake AI response.
- Avoid speculative abstractions and unrelated refactors.

### 5. Verify

Run the narrowest useful checks first, then the complete repository gates:

1. syntax/type checks
2. targeted tests
3. regression tests
4. frontend production build
5. deployment/smoke checks when the change affects runtime behavior

### 6. Decide

**PASS:** all required gates pass and the final diff contains only intentional changes.

**FAIL:** do not declare completion. Capture the failing gate, isolate the root cause, make the smallest repair, and return to Verify.

## Failure repair protocol

```text
failure
  → reproduce
  → classify (code / test / environment / dependency / deployment)
  → isolate root cause
  → smallest repair
  → targeted verification
  → full verification
  → final diff review
```

Do not repeatedly rerun a failing check without changing the condition that caused the failure.

## Completion definition

A task is complete only when:

- requested behavior is implemented;
- relevant failure paths are handled;
- targeted and regression tests pass;
- production build/type/syntax gates pass;
- no secrets or debug artifacts were introduced;
- the final diff is intentional and minimal;
- deployment verification passes when deployment is part of the task.

## AI-specific safety gates

For AI features:

- validate model input and structured output;
- enforce provider timeouts;
- preserve deterministic fallback semantics;
- expose provider failure state honestly;
- keep API keys server-side;
- preserve evidence/context used for recommendations;
- never use career intelligence as an autonomous hiring or rejection decision.

## Change discipline

The loop is not a mandate to keep editing until a green check appears. A green check is meaningful only when it verifies the intended behavior. When a check is inadequate, improve the test or add a focused regression test rather than weakening the implementation to satisfy the check.
