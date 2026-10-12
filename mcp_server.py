from mcp.server import MCPServer

from am_in_core.permissions import PermissionLevel
from am_in_core.runtime import runtime

mcp = MCPServer("Am_in MCP")


@mcp.tool()
def stack_status() -> dict[str, object]:
    """Return the enabled components in the Am_in AI stack."""
    return {
        "project": "Am_in",
        "components": [
            "OpenAI Agents SDK",
            "Browser Use",
            "LiveKit Agents",
            "Model Context Protocol (MCP)",
            "Memory / Permission / Decision / Audit core",
        ],
        "agent_core": runtime.status(),
        "ready_for_external_tools": True,
    }


@mcp.tool()
def evaluate_action(
    action: str,
    confidence: float,
    requested_level: str = "read",
    high_risk: bool = False,
) -> dict[str, object]:
    """Evaluate an action against the shared permission and decision policy."""
    level_map = {
        "read": PermissionLevel.READ,
        "suggest": PermissionLevel.SUGGEST,
        "draft": PermissionLevel.DRAFT,
        "execute_with_approval": PermissionLevel.EXECUTE_WITH_APPROVAL,
        "execute_automatically": PermissionLevel.EXECUTE_AUTOMATICALLY,
    }
    level = level_map.get(requested_level)
    if level is None:
        return {
            "action": action,
            "allowed": False,
            "mode": "analyze_only",
            "reason": "unknown permission level",
            "confidence": confidence,
        }
    return runtime.evaluate_action(
        action,
        confidence=confidence,
        requested_level=level,
        high_risk=high_risk,
    )


@mcp.tool()
def echo(message: str) -> str:
    """Return the provided message. Useful for MCP connectivity tests."""
    return message


@mcp.resource("project://stack")
def project_stack() -> str:
    """Describe the current agent architecture without exposing secrets."""
    return (
        "Am_in uses OpenAI Agents SDK for orchestration, Browser Use for web automation, "
        "LiveKit Agents for realtime voice, MCP for standardized tool/resource connections, "
        "and a shared guarded runtime for memory, permissions, decisions, and audit logging."
    )
