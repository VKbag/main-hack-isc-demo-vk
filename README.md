# ISC Demo Architect

Portable SailPoint **IdentityNow demo** architect package: Cursor agent + **full** allowlisted admin MCP for Hack Day / demo tenants.

## Features

- **Full Cursor demo architect** — `@vk-sailpoint-isc-demo-architect` for ISC design + live demo admin
- **Slash command** — `/isc-demo-architect` (+ fill-in template under `.cursor/prompts/`)
- **Optional lite agent** — `@vk-sailpoint-isc-demo-architect-lite` for read-only verify posture
- **Matching Cursor rules** — `.cursor/rules/` for both profiles
- **Full demo MCP** — sources, identity profiles, transforms, access, governance, workflows, sp-config, accounts, `api_request`
- **Optional lite MCP** — `server_lite.py` (whoami + identity/source reads only)
- **Hard API host allowlist** — locked to `devrel-ga-25104.api.identitynow-demo.com`
- **Destructive guards** — mutate/provision tools require `confirm_destructive=true`
- **OAuth client-credentials auth** — local PAT from gitignored env file
- **Identity tools** — search/get, IP CRUD/mappings, transforms, lifecycle, process identities
- **Access model** — entitlements, access profiles, roles, governance groups, segments
- **Governance** — Search, certification campaigns, SoD policies, work items, AR status
- **Automation** — workflows, trigger subscriptions, sp-config export/import, task status
- **Ops** — accounts enable/disable, activities, connector rules, generic allowlisted `api_request`
- **Local audit trail** — `mcp/**/.audit/` (gitignored)
- **Secrets stay local** — `.env.example` + `~/.cursor/sailpoint-isc-demo.env`

## Demo tenant

| | |
|--|--|
| UI | `https://devrel-ga-25104.identitynow-demo.com` |
| API (MCP allowlist) | `https://devrel-ga-25104.api.identitynow-demo.com` |

MCP refuses any other API host.

## Security

- **Never commit** `SAILPOINT_CLIENT_SECRET`, filled `.env`, or PATs.
- Put credentials in `~/.cursor/sailpoint-isc-demo.env` (`chmod 600`) using `.env.example` as a template.
- Mutations on the demo tenant are real — use `confirm_destructive` deliberately.
- `.gitignore` excludes `.env`, audit logs, and local `mcp.json`.

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

Register MCP in Cursor (see `.cursor/mcp.json.example`). Default entry points at **full** `server.py`.

Reload MCP servers, then in chat:

```
/isc-demo-architect WHOAMI
```

or:

```
@vk-sailpoint-isc-demo-architect demo_whoami then list sources
```

Fill-in template: `.cursor/prompts/isc-demo-architect.template.md`

## MCP tool domains (full `server.py`)

| Domain | Examples |
|--------|----------|
| Tenant | `demo_whoami`, `get_org_config`, `list_connectors` |
| Sources | `list_sources`, `create_source`, `create_delimited_file_source`, schemas, CSV upload/load |
| Identity | IP CRUD, transforms, `search_identities`, `preview_identity`, lifecycle |
| Access | entitlements, access profiles, roles, segments, governance groups |
| Governance | `search`, campaigns, SoD, work items, AR status |
| Automation | workflows, triggers, sp-config, task status |
| Ops | accounts, activities, connector rules, `api_request` |
| Helpers | `spconfig_export_by_names`, manager correlation, role criteria builder |

Lite (`server_lite.py`): `demo_whoami`, identity search/get, list/get sources & identity profiles.

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
