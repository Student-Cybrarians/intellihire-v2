"""Specialist roles used by the IntelliHire project manager."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentRole:
    name: str
    responsibility: str
    outputs: tuple[str, ...]
    requires_human_gate: bool = False


AGENT_ROLES: tuple[AgentRole, ...] = (
    AgentRole(
        "research-agent",
        "Research current technologies, product patterns, risks, and evidence.",
        ("research findings", "trade-offs", "recommendation", "sources"),
    ),
    AgentRole(
        "architect-agent",
        "Define architecture, interfaces, data flow, security, and migration strategy.",
        ("architecture", "contracts", "risks", "acceptance criteria"),
    ),
    AgentRole(
        "developer-agent",
        "Implement planned changes and repairs with minimal regression risk.",
        ("changed files", "implementation summary", "tests", "remaining risks"),
    ),
    AgentRole(
        "qa-agent",
        "Validate unit, integration, regression, security, E2E, and UX behavior.",
        ("test cases", "results", "evidence", "root cause"),
    ),
    AgentRole(
        "devops-agent",
        "Build, deploy, smoke-test, monitor, and safely redeploy or roll back.",
        ("deployment evidence", "health checks", "rollback status"),
        requires_human_gate=True,
    ),
)


def system_prompt(role: AgentRole) -> str:
    gate = (
        "Escalate destructive or production-sensitive actions when a human gate is required."
        if role.requires_human_gate
        else "Escalate destructive or production-sensitive actions to the project manager."
    )
    rules = "\n".join(
        (
            "- Inspect before modifying.",
            "- Follow the task acceptance criteria.",
            "- Report evidence, not assumptions.",
            "- Never silently broaden scope.",
            f"- {gate}",
        )
    )
    return (
        f"You are the IntelliHire {role.name}.\n\n"
        f"Project-manager delegated responsibility: {role.responsibility}\n\n"
        f"Rules:\n{rules}\n\n"
        f"Required outputs: {', '.join(role.outputs)}."
    )
