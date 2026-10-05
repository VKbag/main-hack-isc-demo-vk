"""Workflows, triggers, SP-Config, tasks."""

from __future__ import annotations

import json
from typing import Any

from client import err, get_client, ok, require_destructive


def register(mcp) -> None:
    @mcp.tool()
    def list_workflows(limit: int = 250) -> str:
        """List workflows."""
        try:
            return ok(
                get_client().get(
                    "/workflows",
                    tool="list_workflows",
                    params={"limit": limit},
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_workflow(workflow_id: str) -> str:
        """Get workflow by id."""
        try:
            return ok(
                get_client().get(
                    f"/workflows/{workflow_id}", tool="get_workflow", version="beta"
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_workflow(body_json: str) -> str:
        """Create a workflow (disabled by default recommended in body)."""
        try:
            return ok(
                get_client().post(
                    "/workflows",
                    tool="create_workflow",
                    json_body=json.loads(body_json),
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def update_workflow(
        workflow_id: str, body_json: str, confirm_destructive: bool = False
    ) -> str:
        """Update a workflow. Enabling requires confirm_destructive=true."""
        try:
            body = json.loads(body_json)
            if body.get("enabled") is True:
                require_destructive(
                    confirm_destructive,
                    f"Enabling workflow {workflow_id} may trigger provisioning/actions.",
                )
            return ok(
                get_client().put(
                    f"/workflows/{workflow_id}",
                    tool="update_workflow",
                    json_body=body,
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_trigger_subscriptions(limit: int = 250) -> str:
        """List event trigger subscriptions."""
        try:
            return ok(
                get_client().get(
                    "/trigger-subscriptions",
                    tool="list_trigger_subscriptions",
                    params={"limit": limit},
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def create_trigger_subscription(body_json: str) -> str:
        """Create an event trigger subscription."""
        try:
            return ok(
                get_client().post(
                    "/trigger-subscriptions",
                    tool="create_trigger_subscription",
                    json_body=json.loads(body_json),
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def spconfig_export(body_json: str) -> str:
        """Start an SP-Config export job. Body is ExportPayload JSON."""
        try:
            return ok(
                get_client().post(
                    "/sp-config/export",
                    tool="spconfig_export",
                    json_body=json.loads(body_json),
                    expected=(200, 202),
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def spconfig_import(body_json: str, confirm_destructive: bool = False) -> str:
        """Start an SP-Config import job. Requires confirm_destructive=true (can overwrite demo objects)."""
        try:
            require_destructive(
                confirm_destructive,
                "SP-Config import can create/overwrite objects in demo.",
            )
            return ok(
                get_client().post(
                    "/sp-config/import",
                    tool="spconfig_import",
                    json_body=json.loads(body_json),
                    expected=(200, 202),
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def spconfig_export_status(job_id: str) -> str:
        """Get SP-Config export job status."""
        try:
            return ok(
                get_client().get(
                    f"/sp-config/export/{job_id}",
                    tool="spconfig_export_status",
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def spconfig_download_export(job_id: str) -> str:
        """Download SP-Config export result JSON for a completed job."""
        try:
            return ok(
                get_client().get(
                    f"/sp-config/export/{job_id}/download",
                    tool="spconfig_download_export",
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def list_task_status(limit: int = 50) -> str:
        """List recent task statuses."""
        try:
            return ok(
                get_client().get(
                    "/task-status",
                    tool="list_task_status",
                    params={"limit": limit},
                    version="beta",
                )
            )
        except Exception as exc:
            return err(exc)

    @mcp.tool()
    def get_task_status(task_id: str) -> str:
        """Get task status by id."""
        try:
            return ok(
                get_client().get(
                    f"/task-status/{task_id}", tool="get_task_status", version="beta"
                )
            )
        except Exception as exc:
            return err(exc)
