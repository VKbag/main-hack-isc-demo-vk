---
description: >-
  Run the SailPoint ISC demo architect against the Hack Day demo tenant
  (devrel-ga-25104). Verify with demo MCP; mutates need confirm_destructive.
argument-hint: "[WHOAMI|SEARCH|SPEC|BUILD|APPLY|DEBUG] <goal or identity/source name>"
---

# /isc-demo-architect

Run the **ISC Demo Architect** workflow on the SailPoint IdentityNow **demo** tenant only.

## Activate

1. Agent / rule: `@vk-sailpoint-isc-demo-architect` · `.cursor/rules/vk-sailpoint-isc-demo-architect.mdc`
   - Read-only posture only: `@vk-sailpoint-isc-demo-architect-lite`
2. MCP: `VK-sailpoint-isc-demo` (full) — host allowlisted to  
   `https://devrel-ga-25104.api.identitynow-demo.com`
3. Credentials: `~/.cursor/sailpoint-isc-demo.env` (never echo secrets)

**Do not** use other tenant MCPs from this command.

## Parse user input

User argument or pasted template: **$ARGUMENTS**

If incomplete, show `.cursor/prompts/isc-demo-architect.template.md` and ask for **Phase** + **Goal**.

## Workflow by phase

### Phase `WHOAMI`

1. Call `demo_whoami`.
2. Confirm `demo_lock` / `api_base` is the demo allowlist.
3. Stop — report org name + lock status.

### Phase `SEARCH`

1. Prefer `search_identities` / `list_sources` / `get_identity` / `get_source`.
2. Return ids, names, lifecycle/status — no mutates.

### Phase `SPEC`

1. Design-only: object type, name, fields, ownership, success checks.
2. No JSON apply / no MCP create yet.
3. Flag any destructive blast radius up front.

### Phase `BUILD`

1. Draft API body / JSON Patch / workflow definition as needed.
2. Show the exact MCP tool(s) you will call.
3. **Do not** call mutate tools until Phase `APPLY`.

### Phase `APPLY`

1. Restate blast radius in one sentence.
2. Call mutate tools only with `confirm_destructive=true` when required.
3. Verify with a read tool (`search_identities`, `get_source`, etc.).
4. Report object ids + verify result.

### Phase `DEBUG`

1. Reproduce with read-only tools first.
2. One fix per turn; mutates still need confirm.
3. Prefer account activities / search over guessing.

## Safety — non-negotiable

- Demo API host only — refuse other tenants.
- Never print `SAILPOINT_CLIENT_SECRET` or PATs.
- Destructive / provisioning tools require `confirm_destructive=true`.
- Concise answers: Answer → Verify → Open questions.

User request: $ARGUMENTS
