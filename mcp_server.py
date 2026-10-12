from mcp.server import MCPServer

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
        ],
        "ready_for_external_tools": True,
    }


@mcp.tool()
def echo(message: str) -> str:
    """Return the provided message. Useful for MCP connectivity tests."""
    return message


@mcp.resource("project://stack")
def project_stack() -> str:
    """Describe the current agent architecture without exposing secrets."""
    return (
        "Am_in uses OpenAI Agents SDK for orchestration, Browser Use for web "
        "automation, LiveKit Agents for realtime voice, and MCP for standardized "
        "tool/resource connections."
    )
