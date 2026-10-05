#!/usr/bin/env python3
"""SailPoint ISC demo-tenant MCP — read-only lite tools for architect demos."""

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
    "VK-sailpoint-isc-demo",
    instructions=(
        "Read-only SailPoint ISC demo MCP for tenant "
        f"{ALLOWED_API_BASE}. Tools: demo_whoami, search_identities, get_identity, "
        "list/get sources and identity profiles. API host is hard-allowlisted. "
        "Demo tenant only — not for other ISC environments."
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
    if os.environ.get("SAILPOINT_CLIENT_ID") or (
        env_file.is_file()
        and "your_pat_client_id"
        not in env_file.read_text(encoding="utf-8", errors="ignore")
    ):
        try:
            load_demo_env()
        except DemoGuardError:
            raise
        except Exception:
            pass


_bootstrap_guard()

tenant.register(mcp)
sources.register(mcp)
identity.register(mcp)


if __name__ == "__main__":
    mcp.run()
