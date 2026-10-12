from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .audit import AuditLogger
from .decision import DecisionEngine, DecisionMode
from .memory import MemoryStore
from .permissions import ActionPolicy, PermissionLevel, PermissionPolicy


class AgentRuntime:
    """Shared runtime for memory, permissions, decisions, and audit logging."""

    def __init__(self) -> None:
        self.memory = MemoryStore()
        self.audit = AuditLogger()
        self.decisions = DecisionEngine()
        self.permissions = PermissionPolicy(
            [
                ActionPolicy("read_context", PermissionLevel.READ),
                ActionPolicy("read_external_data", PermissionLevel.READ),
                ActionPolicy("draft_external_action", PermissionLevel.DRAFT),
                ActionPolicy("execute_external_action", PermissionLevel.EXECUTE_WITH_APPROVAL),
            ]
        )

    def evaluate_action(
        self,
        action: str,
        *,
        confidence: float,
        requested_level: PermissionLevel,
        high_risk: bool = False,
    ) -> dict[str, Any]:
        allowed = self.permissions.allows(action, requested_level)
        decision = self.decisions.decide(confidence, high_risk=high_risk)

        if not allowed:
            mode = DecisionMode.ANALYZE_ONLY
            reason = "permission denied"
        elif self.permissions.requires_approval(action):
            mode = DecisionMode.REQUIRE_APPROVAL
            reason = "policy requires approval"
        else:
            mode = decision.mode
            reason = decision.reason

        payload = {
            "action": action,
            "allowed": allowed,
            "mode": mode.value,
            "reason": reason,
            "confidence": confidence,
        }
        self.audit.log("agent", action, mode.value, payload)
        return payload

    def status(self) -> dict[str, Any]:
        return {
            "memory": "sqlite",
            "audit": "jsonl",
            "permission_policy": "deny_unknown",
            "decision_thresholds": {
                "approval": self.decisions.approval_threshold,
                "auto": self.decisions.auto_threshold,
            },
        }


runtime = AgentRuntime()
