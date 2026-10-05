"""Accounts, NELM, machine identities, connector rules."""

from __future__ import annotations

import json
from typing import Any

from client import err, get_client, ok, require_destructive


def register(mcp, *, lite: bool = False) -> None:
    @mcp.tool()
    def list_accounts(filters: str | None = None, limit: int = 250) -> str:
        """List accounts. Optional filters e.g. sourceId eq \"...\""""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(get_client().get("/accounts", tool="list_accounts", params=params))
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_account(account_id: str) -> str:
        """Get account by id."""
        try:
            return ok(get_client().get(f"/accounts/{account_id}", tool="get_account"))
        except Exception as exc:
            return err(exc)

    if lite:
        @mcp.tool()
        def api_request(
            method: str,
            path: str,
            body_json: str | None = None,
            version: str | None = None,
            confirm_destructive: bool = False,
        ) -> str:
            """Escape hatch: call any demo API path under the allowlisted host. Destructive methods need confirm."""
            try:
                m = method.upper()
                if m in ("DELETE", "PUT", "PATCH") or (
                    m == "POST"
                    and any(
                        x in path.lower()
                        for x in ("delete", "import", "disable", "enable", "load-accounts")
                    )
                ):
                    require_destructive(
                        confirm_destructive,
                        f"api_request {m} {path} may mutate demo state.",
                    )
                kwargs: dict[str, Any] = {"tool": "api_request", "version": version}
                if body_json:
                    kwargs["json_body"] = json.loads(body_json)
                return ok(get_client().request(m, path, **kwargs))
            except Exception as exc:
                return err(exc)
        return

    @mcp.tool()
    def disable_account(account_id: str, confirm_destructive: bool = False) -> str:
        """Disable an account. Requires confirm_destructive=true."""
        try:
            require_destructive(confirm_destructive, f"Disables account {account_id}.")
            return ok(
                get_client().post(
                    f"/accounts/{account_id}/disable",
                    tool="disable_account",
                    json_body={},
                    expected=(200, 202),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def enable_account(account_id: str, confirm_destructive: bool = False) -> str:
        """Enable an account. Requires confirm_destructive=true."""
        try:
            require_destructive(confirm_destructive, f"Enables account {account_id}.")
            return ok(
                get_client().post(
                    f"/accounts/{account_id}/enable",
                    tool="enable_account",
                    json_body={},
                    expected=(200, 202),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_account_activities(filters: str | None = None, limit: int = 50) -> str:
        """List account activities."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(
                get_client().get(
                    "/account-activities",
                    tool="list_account_activities",
                    params=params,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_non_employee_sources() -> str:
        """List non-employee (NELM) sources."""
        try:
            return ok(
                get_client().get(
                    "/non-employee-sources",
                    tool="list_non_employee_sources",
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_machine_identities(limit: int = 50) -> str:
        """List machine identities."""
        try:
            return ok(
                get_client().get(
                    "/machine-identities",
                    tool="list_machine_identities",
                    params={"limit": limit},
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_connector_rules() -> str:
        """List connector rules."""
        try:
            return ok(
                get_client().get(
                    "/connector-rules",
                    tool="list_connector_rules",
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_connector_rule(body_json: str) -> str:
        """Create a connector rule (subject to SailPoint cloud rule review for some types)."""
        try:
            return ok(
                get_client().post(
                    "/connector-rules",
                    tool="create_connector_rule",
                    json_body=json.loads(body_json),
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def api_request(
        method: str,
        path: str,
        body_json: str | None = None,
        version: str | None = None,
        confirm_destructive: bool = False,
    ) -> str:
        """Escape hatch: call any demo API path under the allowlisted host. Destructive methods need confirm."""
        try:
            m = method.upper()
            if m in ("DELETE", "PUT", "PATCH") or (
                m == "POST" and any(
                    x in path.lower()
                    for x in ("delete", "import", "disable", "enable", "load-accounts")
                )
            ):
                require_destructive(
                    confirm_destructive,
                    f"api_request {m} {path} may mutate demo state.",
                )
            kwargs: dict[str, Any] = {"tool": "api_request", "version": version}
            if body_json:
                kwargs["json_body"] = json.loads(body_json)
            return ok(get_client().request(m, path, **kwargs))
        except Exception as exc:
            return err(exc)
