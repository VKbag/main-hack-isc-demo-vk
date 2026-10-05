"""Access model: entitlements, access profiles, roles, segments, governance groups."""

from __future__ import annotations

import json
from typing import Any

from client import err, get_client, ok, require_destructive


def register(mcp) -> None:
    @mcp.tool()
    def list_entitlements(filters: str | None = None, limit: int = 250) -> str:
        """List entitlements."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(get_client().get("/entitlements", tool="list_entitlements", params=params))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_entitlement(entitlement_id: str) -> str:
        """Get entitlement by id."""
        try:
            return ok(
                get_client().get(f"/entitlements/{entitlement_id}", tool="get_entitlement")
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def patch_entitlement(entitlement_id: str, patch_json: str) -> str:
        """JSON Patch an entitlement (metadata)."""
        try:
            return ok(
                get_client().patch(
                    f"/entitlements/{entitlement_id}",
                    tool="patch_entitlement",
                    json_body=json.loads(patch_json),
                    headers={"Content-Type": "application/json-patch+json"},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_access_profiles(filters: str | None = None, limit: int = 250) -> str:
        """List access profiles."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(
                get_client().get("/access-profiles", tool="list_access_profiles", params=params)
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_access_profile(access_profile_id: str) -> str:
        """Get access profile by id."""
        try:
            return ok(
                get_client().get(
                    f"/access-profiles/{access_profile_id}", tool="get_access_profile"
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_access_profile(body_json: str) -> str:
        """Create an access profile from JSON body."""
        try:
            return ok(
                get_client().post(
                    "/access-profiles",
                    tool="create_access_profile",
                    json_body=json.loads(body_json),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_access_profile(access_profile_id: str, body_json: str) -> str:
        """Update an access profile (PUT/PATCH via PUT)."""
        try:
            return ok(
                get_client().put(
                    f"/access-profiles/{access_profile_id}",
                    tool="update_access_profile",
                    json_body=json.loads(body_json),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def delete_access_profile(
        access_profile_id: str, confirm_destructive: bool = False
    ) -> str:
        """Delete an access profile. Requires confirm_destructive=true."""
        try:
            require_destructive(
                confirm_destructive, f"Deletes access profile {access_profile_id}."
            )
            get_client().delete(
                f"/access-profiles/{access_profile_id}",
                tool="delete_access_profile",
                expected=(200, 202, 204),
            )
            return ok({"deleted": True, "access_profile_id": access_profile_id})
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_roles(filters: str | None = None, limit: int = 250) -> str:
        """List roles."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(get_client().get("/roles", tool="list_roles", params=params))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_role(role_id: str) -> str:
        """Get role by id."""
        try:
            return ok(get_client().get(f"/roles/{role_id}", tool="get_role"))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_role(body_json: str, confirm_destructive: bool = False) -> str:
        """Create a role. If membershipCriteria may auto-provision, set confirm_destructive=true."""
        try:
            body = json.loads(body_json)
            if body.get("membership") or body.get("accessProfiles"):
                require_destructive(
                    confirm_destructive,
                    "Role create may assign access / trigger provisioning when enabled.",
                )
            return ok(get_client().post("/roles", tool="create_role", json_body=body))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_role(role_id: str, body_json: str, confirm_destructive: bool = False) -> str:
        """Update a role. Confirm if changing membership/provisioning."""
        try:
            body = json.loads(body_json)
            require_destructive(
                confirm_destructive,
                f"Role update {role_id} may change membership and provisioning.",
            )
            return ok(
                get_client().put(f"/roles/{role_id}", tool="update_role", json_body=body)
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def delete_role(role_id: str, confirm_destructive: bool = False) -> str:
        """Delete a role. Requires confirm_destructive=true."""
        try:
            require_destructive(confirm_destructive, f"Deletes role {role_id}.")
            get_client().delete(
                f"/roles/{role_id}", tool="delete_role", expected=(200, 202, 204)
            )
            return ok({"deleted": True, "role_id": role_id})
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_governance_groups(limit: int = 250) -> str:
        """List governance groups (workgroups)."""
        try:
            return ok(
                get_client().get(
                    "/workgroups",
                    tool="list_governance_groups",
                    params={"limit": limit},
                    version="v2024",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_governance_group(body_json: str) -> str:
        """Create a governance group / workgroup."""
        try:
            return ok(
                get_client().post(
                    "/workgroups",
                    tool="create_governance_group",
                    json_body=json.loads(body_json),
                    version="v2024",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_segments(limit: int = 250) -> str:
        """List segments."""
        try:
            return ok(
                get_client().get("/segments", tool="list_segments", params={"limit": limit})
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_segment(body_json: str) -> str:
        """Create a segment."""
        try:
            return ok(
                get_client().post(
                    "/segments", tool="create_segment", json_body=json.loads(body_json)
                )
            )
        except Exception as exc:
            return err(exc)
