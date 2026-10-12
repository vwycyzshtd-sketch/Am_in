from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()

agent = Agent(
    name="Am_in Assistant",
    instructions=(
        "You are the central assistant for the Am_in project. "
        "Be concise, safe, and use tools or specialist agents when appropriate."
    ),
)

if __name__ == "__main__":
    result = Runner.run_sync(agent, "Introduce yourself in one short paragraph.")
    print(result.final_output)
