"""Identity profiles, transforms, identities, lifecycle."""

from __future__ import annotations

import json
from typing import Any

from client import err, get_client, ok, require_destructive

# Generic first+last displayName template (no tenant-specific attribute model).
DISPLAY_NAME_TRANSFORM = {
    "name": "Demo DisplayName",
    "type": "concat",
    "attributes": {
        "values": [
            {"type": "identityAttribute", "attributes": {"name": "firstname"}},
            " ",
            {"type": "identityAttribute", "attributes": {"name": "lastname"}},
        ]
    },
}


def register(mcp, *, lite: bool = False) -> None:
    @mcp.tool()
    def list_identity_profiles(limit: int = 250) -> str:
        """List identity profiles."""
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

    if lite:
        @mcp.tool()
        def preview_identity(identity_profile_id: str, identity_id: str | None = None) -> str:
            """Generate identity profile preview for a sample identity."""
            try:
                body: dict[str, Any] = {"identityProfileId": identity_profile_id}
                if identity_id:
                    body["identityId"] = identity_id
                return ok(
                    get_client().post(
                        "/identity-profiles/identity-preview",
                        tool="preview_identity",
                        json_body=body,
                    )
                )
            except Exception as exc:
                return err(exc)

        @mcp.tool()
        def search_identities(query: str, limit: int = 50) -> str:
            """Search identities using ISC Search API (query e.g. 'attributes.uid:371817')."""
            try:
                body = {
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
        return

    @mcp.tool()
    def create_identity_profile(
        name: str,
        source_id: str,
        description: str = "",
        owner_identity_id: str | None = None,
    ) -> str:
        """Create an identity profile bound to a source (makes source authoritative)."""
        try:
            body: dict[str, Any] = {
                "name": name,
                "description": description or name,
                "authoritativeSource": {"type": "SOURCE", "id": source_id},
            }
            if owner_identity_id:
                body["owner"] = {"type": "IDENTITY", "id": owner_identity_id}
            return ok(
                get_client().post(
                    "/identity-profiles",
                    tool="create_identity_profile",
                    json_body=body,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_identity_profile(identity_profile_id: str, body_json: str) -> str:
        """Full PUT update of an identity profile."""
        try:
            body = json.loads(body_json)
            return ok(
                get_client().put(
                    f"/identity-profiles/{identity_profile_id}",
                    tool="update_identity_profile",
                    json_body=body,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def patch_identity_profile(identity_profile_id: str, patch_json: str) -> str:
        """JSON Patch an identity profile."""
        try:
            body = json.loads(patch_json)
            return ok(
                get_client().patch(
                    f"/identity-profiles/{identity_profile_id}",
                    tool="patch_identity_profile",
                    json_body=body,
                    headers={"Content-Type": "application/json-patch+json"},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_identity_profile_mappings(
        identity_profile_id: str,
        body_json: str,
    ) -> str:
        """Apply identity profile attribute mappings via JSON Patch body (identityAttributeConfig)."""
        try:
            patch = json.loads(body_json)
            return ok(
                get_client().patch(
                    f"/identity-profiles/{identity_profile_id}",
                    tool="update_identity_profile_mappings",
                    json_body=patch,
                    headers={"Content-Type": "application/json-patch+json"},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def delete_identity_profile(
        identity_profile_id: str, confirm_destructive: bool = False
    ) -> str:
        """Delete an identity profile. Requires confirm_destructive=true."""
        try:
            require_destructive(
                confirm_destructive,
                f"Deletes identity profile {identity_profile_id}; identities may be deleted/reassigned.",
            )
            get_client().delete(
                f"/identity-profiles/{identity_profile_id}",
                tool="delete_identity_profile",
                expected=(200, 202, 204),
            )
            return ok({"deleted": True, "identity_profile_id": identity_profile_id})
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def preview_identity(identity_profile_id: str, identity_id: str | None = None) -> str:
        """Generate identity profile preview for a sample identity."""
        try:
            body: dict[str, Any] = {"identityProfileId": identity_profile_id}
            if identity_id:
                body["identityId"] = identity_id
            return ok(
                get_client().post(
                    "/identity-profiles/identity-preview",
                    tool="preview_identity",
                    json_body=body,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_lifecycle_states(identity_profile_id: str) -> str:
        """List lifecycle states for an identity profile."""
        try:
            return ok(
                get_client().get(
                    f"/identity-profiles/{identity_profile_id}/lifecycle-states",
                    tool="list_lifecycle_states",
                    params={"limit": 250},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_lifecycle_state(
        identity_profile_id: str,
        lifecycle_state_id: str,
        body_json: str,
        confirm_destructive: bool = False,
    ) -> str:
        """Update a lifecycle state. If enabling provisioning, set confirm_destructive=true."""
        try:
            body = json.loads(body_json)
            if body.get("enabled") or body.get("accountActions"):
                require_destructive(
                    confirm_destructive,
                    "Lifecycle state update may enable provisioning or account actions.",
                )
            return ok(
                get_client().put(
                    f"/identity-profiles/{identity_profile_id}/lifecycle-states/{lifecycle_state_id}",
                    tool="update_lifecycle_state",
                    json_body=body,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_transforms(name: str | None = None, limit: int = 250) -> str:
        """List transforms."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if name:
                params["filters"] = f'name eq "{name}"'
            return ok(get_client().get("/transforms", tool="list_transforms", params=params))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_transform(transform_id: str) -> str:
        """Get transform by id."""
        try:
            return ok(get_client().get(f"/transforms/{transform_id}", tool="get_transform"))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_transform(body_json: str | None = None, use_display_name_template: bool = False) -> str:
        """Create a transform. Pass body_json, or use_display_name_template for a simple first+last concat."""
        try:
            if use_display_name_template:
                body = DISPLAY_NAME_TRANSFORM
            else:
                if not body_json:
                    raise ValueError("body_json required unless use_display_name_template=true")
                body = json.loads(body_json)
            return ok(get_client().post("/transforms", tool="create_transform", json_body=body))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_transform(transform_id: str, body_json: str) -> str:
        """Update a transform."""
        try:
            return ok(
                get_client().put(
                    f"/transforms/{transform_id}",
                    tool="update_transform",
                    json_body=json.loads(body_json),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def delete_transform(transform_id: str, confirm_destructive: bool = False) -> str:
        """Delete a transform. Requires confirm_destructive=true."""
        try:
            require_destructive(confirm_destructive, f"Deletes transform {transform_id}.")
            get_client().delete(
                f"/transforms/{transform_id}",
                tool="delete_transform",
                expected=(200, 204),
            )
            return ok({"deleted": True, "transform_id": transform_id})
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def search_identities(query: str, limit: int = 50) -> str:
        """Search identities using ISC Search API (query e.g. 'attributes.uid:371817')."""
        try:
            body = {
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

    @mcp.tool()
    def process_identities(identity_ids_json: str) -> str:
        """Process (refresh) a list of identity ids. identity_ids_json is a JSON array of ids."""
        try:
            ids = json.loads(identity_ids_json)
            c = get_client()
            headers = {"X-SailPoint-Experimental": "true"}
            try:
                return ok(
                    c.post(
                        "/identities/process",
                        tool="process_identities",
                        json_body={"identityIds": ids},
                        headers=headers,
                        expected=(200, 202),
                        version="beta",
                    )
                )
            except Exception:
                return ok(
                    c.post(
                        "/identities/process",
                        tool="process_identities",
                        json_body=ids,
                        headers=headers,
                        expected=(200, 202),
                        version="beta",
                    )
                )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_identity_attributes() -> str:
        """List identity attributes configured in the tenant."""
        try:
            return ok(
                get_client().get(
                    "/identity-attributes",
                    tool="list_identity_attributes",
                    params={"limit": 250},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_identity_attribute(body_json: str) -> str:
        """Create a custom identity attribute."""
        try:
            return ok(
                get_client().post(
                    "/identity-attributes",
                    tool="create_identity_attribute",
                    json_body=json.loads(body_json),
                )
            )
        except Exception as exc:
            return err(exc)
