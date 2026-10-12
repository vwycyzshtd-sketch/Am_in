from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class PermissionLevel(IntEnum):
    READ = 10
    SUGGEST = 20
    DRAFT = 30
    EXECUTE_WITH_APPROVAL = 40
    EXECUTE_AUTOMATICALLY = 50


@dataclass(frozen=True)
class ActionPolicy:
    action: str
    level: PermissionLevel


class PermissionPolicy:
    """Central action policy. Defaults to deny for unknown actions."""

    def __init__(self, policies: list[ActionPolicy] | None = None) -> None:
        self._policies = {policy.action: policy.level for policy in policies or []}

    def set(self, action: str, level: PermissionLevel) -> None:
        self._policies[action] = level

    def level_for(self, action: str) -> PermissionLevel | None:
        return self._policies.get(action)

    def allows(self, action: str, requested: PermissionLevel) -> bool:
        configured = self.level_for(action)
        return configured is not None and requested <= configured

    def requires_approval(self, action: str) -> bool:
        configured = self.level_for(action)
        return configured == PermissionLevel.EXECUTE_WITH_APPROVAL
