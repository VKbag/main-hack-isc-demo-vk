"""Tenant safety and org tools."""

from __future__ import annotations

from client import ALLOWED_API_BASE, err, get_client, ok


def register(mcp, *, lite: bool = False) -> None:
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

    if lite:
        return

    @mcp.tool()
    def get_org_config() -> str:
        """Read demo org-config (v2024)."""
        try:
            return ok(get_client().get("/org-config", tool="get_org_config"))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_connectors(filters: str | None = None) -> str:
        """List available connector types in the demo tenant."""
        try:
            params = {"limit": 250}
            if filters:
                params["filters"] = filters
            return ok(get_client().get("/connectors", tool="list_connectors", params=params))
        except Exception as exc:
            return err(exc)
