"""Tenant safety and org tools."""

from __future__ import annotations

from client import ALLOWED_API_BASE, err, get_client, ok


def register(mcp) -> None:
    @mcp.tool()
    def demo_whoami() -> str:
        """Verify demo-tenant auth and org. Fails if API base is not the allowlisted demo host."""
        try:
            c = get_client()
            org = None
            try:
                org = c.get("/org-config", tool="demo_whoami", version="v2024")
            except Exception:
                try:
                    org = c.get("/tenant", tool="demo_whoami", version="beta")
                except Exception as exc2:
                    org = {"note": f"org endpoint limited: {exc2}"}
            return ok(
                {
                    "api_base": c.cfg["api_base"],
                    "allowed_api_base": ALLOWED_API_BASE,
                    "api_version": c.cfg["api_version"],
                    "demo_lock": c.cfg["api_base"] == ALLOWED_API_BASE,
                    "org": org,
                }
            )
        except Exception as exc:
            return err(exc)
