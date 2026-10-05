"""Governance: certifications, SoD, work items, search, access requests."""

from __future__ import annotations

import json
from typing import Any

from client import err, get_client, ok, require_destructive


def register(mcp, *, lite: bool = False) -> None:
    @mcp.tool()
    def search(query: str, indices_json: str = '["identities"]', limit: int = 50) -> str:
        """Generic ISC Search API. indices_json e.g. '[\"identities\",\"accounts\",\"entitlements\"]'."""
        try:
            indices = json.loads(indices_json)
            body = {"indices": indices, "query": {"query": query}}
            return ok(
                get_client().post(
                    "/search",
                    tool="search",
                    json_body=body,
                    params={"limit": limit},
                )
            )
        except Exception as exc:
            return err(exc)

    if lite:
        return

    @mcp.tool()
    def list_campaigns(filters: str | None = None, limit: int = 50) -> str:
        """List certification campaigns."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if filters:
                params["filters"] = filters
            return ok(
                get_client().get(
                    "/campaigns", tool="list_campaigns", params=params, version="v2024"
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_campaign(campaign_id: str) -> str:
        """Get certification campaign by id."""
        try:
            return ok(
                get_client().get(
                    f"/campaigns/{campaign_id}", tool="get_campaign", version="v2024"
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_campaign(body_json: str, confirm_destructive: bool = False) -> str:
        """Create a certification campaign. Requires confirm_destructive=true."""
        try:
            require_destructive(
                confirm_destructive,
                "Creates a certification campaign that may notify reviewers and affect access.",
            )
            return ok(
                get_client().post(
                    "/campaigns",
                    tool="create_campaign",
                    json_body=json.loads(body_json),
                    version="v2024",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_sod_policies(limit: int = 250) -> str:
        """List SoD policies."""
        try:
            return ok(
                get_client().get(
                    "/sod-policies",
                    tool="list_sod_policies",
                    params={"limit": limit},
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_sod_policy(policy_id: str) -> str:
        """Get SoD policy by id."""
        try:
            return ok(
                get_client().get(f"/sod-policies/{policy_id}", tool="get_sod_policy")
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_sod_policy(body_json: str) -> str:
        """Create an SoD policy."""
        try:
            return ok(
                get_client().post(
                    "/sod-policies",
                    tool="create_sod_policy",
                    json_body=json.loads(body_json),
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_work_items(limit: int = 50) -> str:
        """List work items."""
        try:
            return ok(
                get_client().get(
                    "/work-items", tool="list_work_items", params={"limit": limit}
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_access_request_status(
        requested_for: str | None = None, limit: int = 50
    ) -> str:
        """List access request status (admin)."""
        try:
            params: dict[str, Any] = {"limit": limit}
            if requested_for:
                params["requested-for"] = requested_for
            return ok(
                get_client().get(
                    "/access-request-status",
                    tool="list_access_request_status",
                    params=params,
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_campaign_filters(limit: int = 250) -> str:
        """List certification campaign filters."""
        try:
            return ok(
                get_client().get(
                    "/campaign-filters",
                    tool="list_campaign_filters",
                    params={"limit": limit},
                )
            )
        except Exception as exc:
            return err(exc)
