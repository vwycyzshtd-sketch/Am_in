from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DecisionMode(str, Enum):
    ANALYZE_ONLY = "analyze_only"
    REQUIRE_APPROVAL = "require_approval"
    AUTO_EXECUTE = "auto_execute"


@dataclass(frozen=True)
class Decision:
    confidence: float
    mode: DecisionMode
    reason: str


class DecisionEngine:
    """Translate confidence and risk into a controlled execution mode."""

    def __init__(self, auto_threshold: float = 0.90, approval_threshold: float = 0.60) -> None:
        if not 0 <= approval_threshold <= auto_threshold <= 1:
            raise ValueError("thresholds must satisfy 0 <= approval <= auto <= 1")
        self.auto_threshold = auto_threshold
        self.approval_threshold = approval_threshold

    def decide(self, confidence: float, *, high_risk: bool = False) -> Decision:
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if high_risk:
            return Decision(confidence, DecisionMode.REQUIRE_APPROVAL, "high-risk action")
        if confidence >= self.auto_threshold:
            return Decision(confidence, DecisionMode.AUTO_EXECUTE, "high confidence")
        if confidence >= self.approval_threshold:
            return Decision(confidence, DecisionMode.REQUIRE_APPROVAL, "medium confidence")
        return Decision(confidence, DecisionMode.ANALYZE_ONLY, "low confidence")
