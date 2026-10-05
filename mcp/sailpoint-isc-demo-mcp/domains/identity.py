"""Identity search and read tools (read-only)."""

from __future__ import annotations

from typing import Any

from client import err, get_client, ok


def register(mcp) -> None:
    @mcp.tool()
    def list_identity_profiles(limit: int = 250) -> str:
        """List identity profiles in the demo tenant."""
        try:
            return ok(
                get_client().get(
                    "/identity-profiles",
                    tool="list_identity_profiles",
                    params={"limit": limit},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_identity_profile(identity_profile_id: str) -> str:
        """Get identity profile by id."""
        try:
            return ok(
                get_client().get(
                    f"/identity-profiles/{identity_profile_id}",
                    tool="get_identity_profile",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def search_identities(query: str, limit: int = 50) -> str:
        """Search identities (e.g. 'name:Wanda.Watkins' or 'attributes.uid:123')."""
        try:
            body: dict[str, Any] = {
                "indices": ["identities"],
                "query": {"query": query},
                "queryResultFilter": {
                    "includes": [
                        "id",
                        "name",
                        "displayName",
                        "email",
                        "attributes",
                        "identityProfile",
                        "lifecycleState",
                        "status",
                    ]
                },
            }
            return ok(
                get_client().post(
                    "/search",
                    tool="search_identities",
                    json_body=body,
                    params={"limit": limit},
                    version="v2024",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_identity(identity_id: str) -> str:
        """Get identity by id."""
        try:
            return ok(get_client().get(f"/identities/{identity_id}", tool="get_identity"))
        except Exception as exc:
            return err(exc)
