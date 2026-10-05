"""Source, schema, and aggregation tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from client import err, get_client, ok, require_destructive
from schema_from_csv import schema_payload_from_csv


def register(mcp, *, lite: bool = False) -> None:
    @mcp.tool()
    def list_sources(filters: str | None = None, limit: int = 250) -> str:
        """List sources in demo. Optional ISC filters string."""
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

    if lite:
        return

    @mcp.tool()
    def create_source(body_json: str, provision_as_csv: bool = False) -> str:
        """Create a source from JSON body. Set provision_as_csv=true for Delimited File."""
        try:
            body = json.loads(body_json)
            params = {"provisionAsCsv": "true"} if provision_as_csv else None
            return ok(
                get_client().post(
                    "/sources",
                    tool="create_source",
                    json_body=body,
                    params=params,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_delimited_file_source(
        name: str,
        owner_identity_id: str,
        description: str = "Temporary authoritative HR flat file (demo)",
        owner_name: str = "",
    ) -> str:
        """Create a Delimited File source (provisionAsCsv=true). Requires owner identity id."""
        try:
            owner: dict[str, Any] = {"type": "IDENTITY", "id": owner_identity_id}
            if owner_name:
                owner["name"] = owner_name
            body = {
                "name": name,
                "description": description,
                "owner": owner,
                "connector": "delimited-file",
            }
            return ok(
                get_client().post(
                    "/sources",
                    tool="create_delimited_file_source",
                    json_body=body,
                    params={"provisionAsCsv": "true"},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_source(source_id: str, body_json: str) -> str:
        """Full update of a source (PUT)."""
        try:
            body = json.loads(body_json)
            return ok(
                get_client().put(
                    f"/sources/{source_id}",
                    tool="update_source",
                    json_body=body,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def patch_source(source_id: str, patch_json: str) -> str:
        """JSON Patch a source (RFC 6902 array)."""
        try:
            body = json.loads(patch_json)
            return ok(
                get_client().patch(
                    f"/sources/{source_id}",
                    tool="patch_source",
                    json_body=body,
                    headers={"Content-Type": "application/json-patch+json"},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def delete_source(source_id: str, confirm_destructive: bool = False) -> str:
        """Delete a source. Requires confirm_destructive=true."""
        try:
            require_destructive(
                confirm_destructive,
                f"Deletes source {source_id} and related aggregation state in demo.",
            )
            get_client().delete(
                f"/sources/{source_id}",
                tool="delete_source",
                expected=(200, 202, 204),
            )
            return ok({"deleted": True, "source_id": source_id})
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_source_schemas(source_id: str) -> str:
        """List schemas for a source."""
        try:
            return ok(
                get_client().get(f"/sources/{source_id}/schemas", tool="get_source_schemas")
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_account_schema(source_id: str, schema_id: str) -> str:
        """Get a specific source schema."""
        try:
            return ok(
                get_client().get(
                    f"/sources/{source_id}/schemas/{schema_id}",
                    tool="get_account_schema",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def put_account_schema_from_csv(
        source_id: str,
        csv_path: str,
        schema_id: str | None = None,
    ) -> str:
        """Replace/update account schema attributes from a CSV header row (csv_path required)."""
        try:
            c = get_client()
            built = schema_payload_from_csv(csv_path)
            schemas = c.get(f"/sources/{source_id}/schemas", tool="put_account_schema_from_csv")
            account_schema = None
            if isinstance(schemas, list):
                for s in schemas:
                    if s.get("name") == "account" or s.get("nativeObjectType") == "account":
                        account_schema = s
                        break
                if account_schema is None and schemas:
                    account_schema = schemas[0]
            sid = schema_id or (account_schema or {}).get("id")
            if not sid:
                raise RuntimeError("Could not resolve account schema id for source")

            # Use PUT schema update with attributes from CSV
            current = c.get(
                f"/sources/{source_id}/schemas/{sid}",
                tool="put_account_schema_from_csv",
            )
            payload = dict(current) if isinstance(current, dict) else {}
            payload["attributes"] = built["attributes"]
            payload["identityAttribute"] = "WORKER_ID"
            payload["displayAttribute"] = "WORKER_ID"
            result = c.put(
                f"/sources/{source_id}/schemas/{sid}",
                tool="put_account_schema_from_csv",
                json_body=payload,
            )
            return ok(
                {
                    "source_id": source_id,
                    "schema_id": sid,
                    "attribute_count": len(built["attributes"]),
                    "headers": built["headers"],
                    "csv_path": built["csv_path"],
                    "result": result,
                }
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def upload_accounts_csv(source_id: str, csv_path: str, disable_optimization: bool = False) -> str:
        """Upload a CSV and run account aggregation for a Delimited File source."""
        try:
            path = Path(csv_path)
            if not path.is_file():
                raise FileNotFoundError(f"CSV not found: {path}")
            c = get_client()
            # First upload file to source (connector file)
            with path.open("rb") as fh:
                files = {"file": (path.name, fh, "text/csv")}
                # Some tenants use import-accounts with multipart; try load-accounts pattern
                try:
                    upload = c.request(
                        "POST",
                        f"/sources/{source_id}/load-accounts",
                        tool="upload_accounts_csv",
                        files={
                            "file": (path.name, path.read_bytes(), "text/csv"),
                            **(
                                {"disableOptimization": (None, "true")}
                                if disable_optimization
                                else {}
                            ),
                        },
                        expected=(200, 202),
                    )
                    return ok({"source_id": source_id, "aggregation": upload})
                except Exception as primary:
                    # Fallback: put-account-file then load
                    c.request(
                        "POST",
                        f"/sources/{source_id}/connectors/files",
                        tool="upload_accounts_csv",
                        files={"file": (path.name, path.read_bytes(), "text/csv")},
                        expected=(200, 201, 202),
                    )
                    agg = c.post(
                        f"/sources/{source_id}/load-accounts",
                        tool="upload_accounts_csv",
                        json_body={"disableOptimization": disable_optimization},
                        expected=(200, 202),
                    )
                    return ok(
                        {
                            "source_id": source_id,
                            "note": f"load-accounts multipart failed ({primary}); used file upload fallback",
                            "aggregation": agg,
                        }
                    )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def load_accounts(source_id: str, disable_optimization: bool = False) -> str:
        """Trigger account aggregation for a direct-connect source."""
        try:
            return ok(
                get_client().post(
                    f"/sources/{source_id}/load-accounts",
                    tool="load_accounts",
                    json_body={"disableOptimization": disable_optimization},
                    expected=(200, 202),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_managed_clusters() -> str:
        """List VA / managed clusters (demo)."""
        try:
            return ok(
                get_client().get(
                    "/managed-clusters",
                    tool="list_managed_clusters",
                    params={"limit": 250},
                    version="v2024",
                )
            )
        except Exception as exc:
            return err(exc)
