# Am_in Web + Docker Deployment

This deployment adds a mobile-friendly control plane for the compressed MCP process.

## What runs

- `uvicorn web_control:app` exposes the web control panel.
- The panel starts/stops `run_mcp_compressed.py` inside the same container.
- `mcp-compressor` remains configured through `MCP_COMPRESSION_LEVEL`.
- Secrets are injected through environment variables and are not committed.

## Required environment variables

Set at minimum:

```env
CONTROL_USER=amin
CONTROL_PASSWORD=<strong-random-password>
MCP_COMPRESSION_LEVEL=medium
```

Set the project credentials only when their corresponding components are used:

```env
OPENAI_API_KEY=
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
```

## Local Docker

```bash
cp .env.example .env
# Fill CONTROL_PASSWORD and any required API credentials.
docker compose up -d --build
```

Open `http://localhost:8080` and authenticate with `CONTROL_USER` / `CONTROL_PASSWORD`.

## Phone usage

An iPhone does not run this Docker container directly. The container runs on a remote host/VPS; the phone opens the HTTPS deployment URL and controls the MCP process from the browser.

Available controls:

- Start MCP
- Stop MCP
- Restart MCP
- View process status, uptime and compression level
- View the last 300 log lines

## Security

- Never commit `.env` or API keys.
- Use HTTPS on the public deployment.
- Use a strong unique `CONTROL_PASSWORD`.
- The control API deliberately does not expose arbitrary shell execution.
- `/health` is public and returns only service health; control/status/log endpoints require HTTP Basic authentication.

## Railway

`railway.toml` is included and the Dockerfile is the build source. Configure the required environment variables in the Railway service and expose the generated HTTPS domain. Railway supplies `PORT`; the container respects it automatically.
