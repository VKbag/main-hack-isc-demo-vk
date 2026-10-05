#!/usr/bin/env python3
"""Read-only lite demo MCP (~verify tools only). Prefer server.py for full architect."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastmcp import FastMCP

from client import ALLOWED_API_BASE, DemoGuardError, load_demo_env
from domains import identity, sources, tenant

mcp = FastMCP(
    "VK-sailpoint-isc-demo-lite",
    instructions=(
        "Read-only SailPoint ISC demo MCP for "
        f"{ALLOWED_API_BASE}. Tools: demo_whoami, search/get identity, "
        "list/get sources and identity profiles. Use server.py for full CRUD."
    ),
)


def _bootstrap_guard() -> None:
    explicit = os.environ.get("SAILPOINT_API_BASE")
    if explicit and explicit.rstrip("/") != ALLOWED_API_BASE:
        raise DemoGuardError(
            f"Refusing API base {explicit!r}. Only {ALLOWED_API_BASE!r} is allowed."
        )
    env_file = Path(
        os.environ.get(
            "SAILPOINT_DEMO_ENV_FILE",
            str(Path.home() / ".cursor" / "sailpoint-isc-demo.env"),
        )
    )
    if os.environ.get("SAILPOINT_CLIENT_ID") or env_file.is_file():
        try:
            load_demo_env()
        except DemoGuardError:
            raise
        except Exception:
            pass


_bootstrap_guard()

tenant.register(mcp, lite=True)
sources.register(mcp, lite=True)
identity.register(mcp, lite=True)


if __name__ == "__main__":
    mcp.run()
