# Agents in this workspace

This folder is a **standalone Cursor project** for the SailPoint IdentityNow Hack Day demo tenant.

## Primary

- **`@vk-sailpoint-isc-demo-architect`** — full demo admin (CRUD with `confirm_destructive`)
- Slash command: **`/isc-demo-architect`**

## Optional read-only

- **`@vk-sailpoint-isc-demo-architect-lite`** — verify only

## MCP

- `VK-sailpoint-isc-demo` → `mcp/sailpoint-isc-demo-mcp/server.py`
- Credentials: `~/.cursor/sailpoint-isc-demo.env` (never commit)

Do not point tools at other ISC tenants from this workspace.
