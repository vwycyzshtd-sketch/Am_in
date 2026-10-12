from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    action: str
    outcome: str
    metadata: dict[str, Any]
    timestamp: str


class AuditLogger:
    """Append-only JSONL audit log for agent decisions and tool actions."""

    def __init__(self, path: str = "data/audit.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, actor: str, action: str, outcome: str, metadata: dict[str, Any] | None = None) -> AuditEvent:
        event = AuditEvent(
            actor=actor,
            action=action,
            outcome=outcome,
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        return event
