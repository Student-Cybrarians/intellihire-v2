# Project Manager Agent Architecture

## Purpose

The IntelliHire Project Manager is the control plane for software delivery. It coordinates research, planning, design, implementation, QA, deployment, repair, and optimization without replacing the domain modules or AI response layer.

## State machine

```text
DISCOVERING
  -> RESEARCHING
  -> PLANNING
  -> DESIGNING
  -> BUILDING
  -> TESTING
  -> DEPLOYING
  -> VERIFYING
  -> OPTIMIZING
  -> COMPLETE
```

Failure paths:

```text
BUILDING -> REPAIRING
TESTING -> REPAIRING
DEPLOYING -> ROLLBACK | REPAIRING
VERIFYING -> REPAIRING
REPAIRING -> RESEARCHING
```

## Pass behavior

A passed test must produce evidence. The manager then checks acceptance criteria and regression impact, records the result, and may generate research-backed feature candidates. Features are prioritized rather than automatically implemented.

## Fail behavior

A failed test freezes feature expansion for the affected component. The manager requires reproduction, failure classification, root-cause analysis, repair research, a repair plan, implementation, affected-test rerun, regression testing, and deployment verification where applicable.

## Boundaries

The project-manager package is provider neutral. It does not execute shell commands, modify production directly, store secrets, or make autonomous hiring/rejection decisions. It is compatible with the repository's backend boundaries and existing CI/CD.

## Munder Difflin alignment

The design borrows the useful supervisor concepts from Munder Difflin: an orchestrator owns routing and task state, specialist agents perform focused work, and critical actions can escalate to a human gate. IntelliHire keeps those concepts lightweight and aligned with its existing web/backend architecture.
