from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

from am_in_core.runtime import runtime

load_dotenv()


@function_tool
def agent_core_status() -> dict[str, object]:
    """Return the current memory, permission, decision, and audit runtime status."""
    return runtime.status()


agent = Agent(
    name="Am_in Assistant",
    instructions=(
        "You are the central assistant for the Am_in project. "
        "Use tools when appropriate. Treat external actions as controlled actions: "
        "read-only work may proceed when permitted, but consequential external actions "
        "must go through the project permission and approval policy before execution."
    ),
    tools=[agent_core_status],
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "Check the agent core status, then introduce yourself briefly.")
    print(result.final_output)
