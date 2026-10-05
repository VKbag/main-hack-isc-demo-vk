"""Demand-driven gap tools: lifecycle enable, manager correlation, process, sp-config by name."""

from __future__ import annotations

import json
from typing import Any

from client import err, get_client, ok, require_destructive


def register(mcp, *, lite: bool = False) -> None:
    @mcp.tool()
    def spconfig_export_by_names(
        source_names_json: str = "[]",
        identity_profile_names_json: str = "[]",
        transform_name_prefix: str = "",
        role_names_json: str = "[]",
        include_types_json: str | None = None,
    ) -> str:
        """
        Resolve object names to ids and start an SP-Config export job (demo).
        include_types_json defaults to SOURCE,IDENTITY_PROFILE,TRANSFORM,ROLE.
        """
        try:
            c = get_client()
            object_refs: list[dict[str, Any]] = []

            for name in json.loads(source_names_json):
                sources = c.get(
                    "/sources",
                    tool="spconfig_export_by_names",
                    params={"filters": f'name eq "{name}"', "limit": 5},
                )
                if sources:
                    object_refs.append(
                        {"id": sources[0]["id"], "type": "SOURCE", "name": name}
                    )

            ips = c.get(
                "/identity-profiles",
                tool="spconfig_export_by_names",
                params={"limit": 250},
            )
            wanted_ips = set(json.loads(identity_profile_names_json))
            if isinstance(ips, list):
                for ip in ips:
                    if ip.get("name") in wanted_ips:
                        object_refs.append(
                            {
                                "id": ip["id"],
                                "type": "IDENTITY_PROFILE",
                                "name": ip.get("name"),
                            }
                        )

            if transform_name_prefix:
                transforms = c.get(
                    "/transforms",
                    tool="spconfig_export_by_names",
                    params={"limit": 250},
                )
                if isinstance(transforms, list):
                    for t in transforms:
                        if str(t.get("name", "")).startswith(transform_name_prefix):
                            object_refs.append(
                                {
                                    "id": t["id"],
                                    "type": "TRANSFORM",
                                    "name": t.get("name"),
                                }
                            )

            for name in json.loads(role_names_json):
                roles = c.get(
                    "/roles",
                    tool="spconfig_export_by_names",
                    params={"filters": f'name eq "{name}"', "limit": 5},
                )
                if roles:
                    object_refs.append(
                        {"id": roles[0]["id"], "type": "ROLE", "name": name}
                    )

            types = (
                json.loads(include_types_json)
                if include_types_json
                else ["SOURCE", "IDENTITY_PROFILE", "TRANSFORM", "ROLE"]
            )
            # Prefer object-level export when ids known; else type export
            if object_refs:
                # beta export payload variants differ; use includeTypes + objectOptions when possible
                body: dict[str, Any] = {
                    "description": "Demo MCP export by names",
                    "includeTypes": types,
                    "objectOptions": {},
                }
                # Attach ids per type
                by_type: dict[str, list[str]] = {}
                for ref in object_refs:
                    by_type.setdefault(ref["type"], []).append(ref["id"])
                for t, ids in by_type.items():
                    body["objectOptions"][t] = {
                        "includedIds": ids,
                        "includedNames": [],
                    }
            else:
                body = {
                    "description": "Demo MCP export types only",
                    "includeTypes": types,
                }

            job = c.post(
                "/sp-config/export",
                tool="spconfig_export_by_names",
                json_body=body,
                expected=(200, 202),
                version="beta",
            )
            return ok({"job": job, "resolved_objects": object_refs, "payload": body})
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def apply_identity_profile_changes(identity_profile_id: str) -> str:
        """
        Trigger identity refresh for identities under a profile via search + process
        (experimental header). Use after mapping changes.
        """
        try:
            c = get_client()
            ip = c.get(
                f"/identity-profiles/{identity_profile_id}",
                tool="apply_identity_profile_changes",
            )
            name = ip.get("name")
            hits = c.post(
                "/search",
                tool="apply_identity_profile_changes",
                json_body={
                    "indices": ["identities"],
                    "query": {"query": f'identityProfile.id:"{identity_profile_id}"'},
                    "queryResultFilter": {"includes": ["id", "name"]},
                },
                params={"limit": 250},
            )
            ids = [h["id"] for h in hits] if isinstance(hits, list) else []
            if not ids:
                return ok(
                    {
                        "identity_profile_id": identity_profile_id,
                        "name": name,
                        "processed": 0,
                        "note": "No identities found for profile (or search lag).",
                    }
                )
            result = c.post(
                "/identities/process",
                tool="apply_identity_profile_changes",
                json_body={"identityIds": ids},
                headers={"X-SailPoint-Experimental": "true"},
                expected=(200, 202),
                version="beta",
            )
            return ok(
                {
                    "identity_profile_id": identity_profile_id,
                    "name": name,
                    "processed": len(ids),
                    "result": result,
                }
            )
        except Exception as exc:
            # Fallback: some tenants accept a raw list with experimental header
            try:
                c = get_client()
                hits = c.post(
                    "/search",
                    tool="apply_identity_profile_changes",
                    json_body={
                        "indices": ["identities"],
                        "query": {
                            "query": f'identityProfile.id:"{identity_profile_id}"'
                        },
                        "queryResultFilter": {"includes": ["id"]},
                    },
                    params={"limit": 250},
                )
                ids = [h["id"] for h in hits] if isinstance(hits, list) else []
                result = c.post(
                    "/identities/process",
                    tool="apply_identity_profile_changes",
                    json_body=ids,
                    headers={"X-SailPoint-Experimental": "true"},
                    expected=(200, 202),
                    version="beta",
                )
                return ok(
                    {
                        "identity_profile_id": identity_profile_id,
                        "processed": len(ids),
                        "result": result,
                        "note": "Used list-body fallback",
                    }
                )
            except Exception as exc2:
                return err(exc2 if str(exc2) else exc)

    if lite:
        return

    @mcp.tool()
    def set_manager_correlation(
        source_id: str,
        account_attribute_name: str = "MANAGER_ID",
        identity_attribute_name: str = "uid",
    ) -> str:
        """Set source managerCorrelationMapping (account attr → identity attr)."""
        try:
            c = get_client()
            c.patch(
                f"/sources/{source_id}",
                tool="set_manager_correlation",
                json_body=[
                    {
                        "op": "replace",
                        "path": "/managerCorrelationMapping",
                        "value": {
                            "accountAttributeName": account_attribute_name,
                            "identityAttributeName": identity_attribute_name,
                        },
                    }
                ],
                headers={"Content-Type": "application/json-patch+json"},
            )
            src = c.get(f"/sources/{source_id}", tool="set_manager_correlation")
            return ok(
                {
                    "source_id": source_id,
                    "managerCorrelationMapping": src.get("managerCorrelationMapping"),
                }
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_manager_correlation(source_id: str) -> str:
        """Read manager correlation mapping for a source."""
        try:
            src = get_client().get(
                f"/sources/{source_id}", tool="get_manager_correlation"
            )
            return ok(
                {
                    "source_id": source_id,
                    "managerCorrelationMapping": src.get("managerCorrelationMapping"),
                    "managerCorrelationRule": src.get("managerCorrelationRule"),
                }
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def enable_lifecycle_state(
        identity_profile_id: str,
        technical_name: str,
        enabled: bool = True,
        confirm_destructive: bool = False,
    ) -> str:
        """
        Enable/disable a lifecycle state by technicalName (active, preHire, leaveOfAbsence, terminated).
        Enabling can drive provisioning — requires confirm_destructive=true when enabled=true.
        """
        try:
            if enabled:
                require_destructive(
                    confirm_destructive,
                    f"Enabling lifecycle state '{technical_name}' may trigger account actions/provisioning.",
                )
            c = get_client()
            states = c.get(
                f"/identity-profiles/{identity_profile_id}/lifecycle-states",
                tool="enable_lifecycle_state",
                params={"limit": 50},
            )
            match = next(
                (
                    s
                    for s in (states or [])
                    if s.get("technicalName") == technical_name
                    or s.get("name", "").replace(" ", "").lower()
                    == technical_name.lower()
                ),
                None,
            )
            if not match:
                raise RuntimeError(
                    f"Lifecycle state not found: {technical_name}. "
                    f"Available: {[(s.get('technicalName'), s.get('enabled')) for s in (states or [])]}"
                )
            body = dict(match)
            body["enabled"] = enabled
            updated = c.put(
                f"/identity-profiles/{identity_profile_id}/lifecycle-states/{match['id']}",
                tool="enable_lifecycle_state",
                json_body=body,
            )
            return ok(
                {
                    "identity_profile_id": identity_profile_id,
                    "technicalName": updated.get("technicalName") or technical_name,
                    "enabled": updated.get("enabled"),
                    "id": updated.get("id") or match["id"],
                }
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def build_standard_role_criteria(
        identity_attribute: str,
        operation: str = "EQUALS",
        value: str = "",
    ) -> str:
        """
        Build a STANDARD role membership criteria JSON snippet for create_role/update_role.
        operation examples: EQUALS, NOT_EQUALS, CONTAINS.
        """
        try:
            criteria = {
                "type": "STANDARD",
                "criteria": {
                    "operation": operation,
                    "key": {
                        "type": "IDENTITY",
                        "property": f"attribute.{identity_attribute}",
                        "sourceId": None,
                    },
                    "stringValue": value,
                },
            }
            return ok(criteria)
        except Exception as exc:
            return err(exc)
