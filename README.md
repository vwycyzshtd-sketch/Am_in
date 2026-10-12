# Am_in AI Agent

Modular AI assistant stack combining:

- OpenAI Agents SDK for agent orchestration
- Browser Use for browser automation
- LiveKit Agents for realtime voice/WebRTC

## Requirements

- Python 3.12
- `uv` recommended
- OpenAI API key
- LiveKit project credentials for voice sessions

## Install

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai-agents browser-use "livekit-agents[openai]" python-dotenv
```

## Environment

Copy the example file:

```bash
cp .env.example .env
```

Then set:

```env
OPENAI_API_KEY=
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
```

Never commit `.env` or API keys.

## LiveKit voice agent

The realtime voice entrypoint is:

```bash
python livekit_agent.py dev
```

It uses the OpenAI realtime model through the LiveKit OpenAI plugin and the `marin` voice. The agent is instructed to help with restaurant reservation planning and to confirm details before any booking action.

## Architecture

```text
User
  |
  +--> OpenAI Agents SDK --> orchestration/tools
  |
  +--> Browser Use -------> browser automation
  |
  +--> LiveKit Agents ----> realtime voice/WebRTC
                              |
                              +--> OpenAI realtime model
```

## Safety / actions

This repository does not perform real restaurant bookings by itself. Any external action should be implemented as a separate tool and should require explicit confirmation before execution.
