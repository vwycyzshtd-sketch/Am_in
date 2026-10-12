"""Run the Am_in MCP server through Atlassian's mcp-compressor proxy.

Usage:
    uv run python run_mcp_compressed.py

Optional environment variable:
    MCP_COMPRESSION_LEVEL=low|medium|high|max
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path


LOG = logging.getLogger("am_in.mcp_compressed")
ALLOWED_LEVELS = {"low", "medium", "high", "max"}
DEFAULT_LEVEL = "medium"


def _compression_level() -> str:
    level = os.getenv("MCP_COMPRESSION_LEVEL", DEFAULT_LEVEL).strip().lower()
    if level not in ALLOWED_LEVELS:
        allowed = ", ".join(sorted(ALLOWED_LEVELS))
        raise ValueError(
            f"Invalid MCP_COMPRESSION_LEVEL={level!r}. Expected one of: {allowed}."
        )
    return level


def _require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise RuntimeError(
            f"Required executable {name!r} was not found. Run `uv sync` in the project root first."
        )
    return executable


def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    project_root = Path(__file__).resolve().parent
    server_file = project_root / "mcp_server.py"
    if not server_file.is_file():
        LOG.error("MCP server file not found: %s", server_file)
        return 2

    try:
        level = _compression_level()
        compressor = _require_executable("mcp-compressor")
        mcp_cli = _require_executable("mcp")
    except (RuntimeError, ValueError) as exc:
        LOG.error("%s", exc)
        return 2

    command = [
        compressor,
        "-c",
        level,
        "--",
        mcp_cli,
        "run",
        str(server_file),
    ]

    LOG.info("Starting compressed MCP proxy (compression=%s)", level)
    try:
        completed = subprocess.run(command, cwd=project_root, check=False)
    except OSError as exc:
        LOG.exception("Failed to start compressed MCP proxy: %s", exc)
        return 1

    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
