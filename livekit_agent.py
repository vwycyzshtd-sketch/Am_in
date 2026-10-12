from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import openai

load_dotenv()

server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime-2.1",
            voice="marin",
        )
    )

    agent = Agent(
        instructions=(
            "You are a helpful realtime voice assistant. "
            "Help the caller plan a restaurant reservation and confirm all details "
            "before any booking action is performed."
        )
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(
        instructions="Greet the caller briefly and ask how you can help with the reservation."
    )


if __name__ == "__main__":
    cli.run_app(server)
