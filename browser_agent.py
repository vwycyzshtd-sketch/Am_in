import asyncio
from dotenv import load_dotenv
from browser_use import Agent, ChatOpenAI

load_dotenv()

async def main() -> None:
    llm = ChatOpenAI(model="gpt-5.6-luna", reasoning_effort="high")
    agent = Agent(
        task="Open https://example.com and report the page title.",
        llm=llm,
    )
    history = await agent.run()
    print(history.final_result())

if __name__ == "__main__":
    asyncio.run(main())
