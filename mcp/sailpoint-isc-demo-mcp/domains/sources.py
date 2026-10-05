"""Source read tools (read-only)."""

from __future__ import annotations

from typing import Any

from client import err, get_client, ok


def register(mcp) -> None:
    @mcp.tool()
    def list_sources(filters: str | None = None, limit: int = 250) -> str:
        """List sources. Optional ISC filters string."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(get_client().get("/sources", tool="list_sources", params=params))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_source(source_id: str) -> str:
        """Get a source by id."""
        try:
            return ok(get_client().get(f"/sources/{source_id}", tool="get_source"))
        except Exception as exc:
            return err(exc)
