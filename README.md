# ISC Demo Architect (Lite)

Portable SailPoint **IdentityNow demo** architect package: Cursor agent + read-only MCP for Hack Day / demo tenants.

Includes:

- Cursor agent: `@vk-sailpoint-isc-demo-architect-lite`
- Cursor rule (same guidance)
- Thin **read-only** MCP server hard-allowlisted to the demo API host

## Demo tenant

| | |
|--|--|
| UI | `https://devrel-ga-25104.identitynow-demo.com` |
| API (MCP allowlist) | `https://devrel-ga-25104.api.identitynow-demo.com` |

MCP refuses any other API host.

## Security

- **Never commit** `SAILPOINT_CLIENT_SECRET`, filled `.env`, or PATs.
- Put credentials in `~/.cursor/sailpoint-isc-demo.env` (`chmod 600`) using `.env.example` as a template.
- `.gitignore` excludes `.env`, audit logs, and local `mcp.json`.

If credentials were pasted into chat or tickets, **rotate the PAT** in the demo tenant.

## Setup

```bash
cd mcp/sailpoint-isc-demo-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bash
cp .env.example ~/.cursor/sailpoint-isc-demo.env
# edit with real client id/secret
chmod 600 ~/.cursor/sailpoint-isc-demo.env
```

Register MCP in Cursor (see `.cursor/mcp.json.example`). Use absolute paths if your Cursor build does not expand `${workspaceFolder}`.

Reload MCP servers, then in Agent chat:

```
@vk-sailpoint-isc-demo-architect-lite demo_whoami then search for Wanda.Watkins
```

## MCP tools (v1 read-only)

| Tool | Purpose |
|------|---------|
| `demo_whoami` | Auth + org + allowlist check |
| `search_identities` | ISC Search on identities |
| `get_identity` | Identity by id |
| `list_identity_profiles` / `get_identity_profile` | Identity profiles |
| `list_sources` / `get_source` | Sources |

## Verify without Cursor

```bash
cd mcp/sailpoint-isc-demo-mcp
SAILPOINT_DEMO_ENV_FILE="$HOME/.cursor/sailpoint-isc-demo.env" \
  ./venv/bin/python -c "
from client import get_client
c = get_client()
print('api_base', c.cfg['api_base'])
print(c.get('/org-config', tool='smoke', version='v2024'))
"
```

## License / ownership

Personal/demo scaffolding for SailPoint Hack Day. Do not store production secrets or customer data here.
