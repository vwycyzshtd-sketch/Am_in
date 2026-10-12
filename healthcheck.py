from __future__ import annotations

import importlib
import os
import sys

REQUIRED_ENV = (
    "OPENAI_API_KEY",
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
)

MODULES = (
    ("agents", "OpenAI Agents SDK"),
    ("browser_use", "Browser Use"),
    ("livekit.agents", "LiveKit Agents"),
    ("livekit.plugins.openai", "LiveKit OpenAI plugin"),
)


def main() -> int:
    ok = True
    print("== Dependency check ==")
    for module_name, label in MODULES:
        try:
            importlib.import_module(module_name)
            print(f"[OK] {label}")
        except Exception as exc:
            ok = False
            print(f"[FAIL] {label}: {exc}")

    print("\n== Environment check ==")
    for name in REQUIRED_ENV:
        value = os.getenv(name)
        if value:
            print(f"[OK] {name} is set")
        else:
            ok = False
            print(f"[MISSING] {name}")

    print("\nNo secret values are printed by this script.")
    if ok:
        print("Environment is ready for a real OpenAI + LiveKit connection test.")
        return 0

    print("Setup is incomplete. Add the missing environment variables and run again.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
