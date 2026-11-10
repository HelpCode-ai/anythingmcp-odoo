# AnythingMCP for Odoo

Use Odoo in Claude, ChatGPT and Copilot. This Odoo module adds an **AI Assistants** block to
*Settings → General Settings* that connects your Odoo to [AnythingMCP](https://anythingmcp.com)
in three steps:

1. **Create an API key** opens Odoo's own dialog for a new API key of your user.
2. **Open AnythingMCP** opens the AnythingMCP setup with your Odoo address and database name
   already filled in (on Odoo 17 and 18 also the user id), plus `source=odoo_module` so
   AnythingMCP can count the setups opened from here. You paste the key there; it is never
   part of the link.
3. AnythingMCP checks the key against your Odoo, then shows how to add it to your assistant.

The module adds no models, stores nothing and calls no external service by itself.

From `19.0` on it is a data module: no Python code, only a view and two server actions
(`data/actions.xml`). Odoo Online runs no third-party Python, but it imports data modules:
turn on developer mode, then *Apps → Import Module* and upload the module's zip. On Odoo.sh
and on-premise it installs from the addons path like any module.

| Branch | Odoo | AnythingMCP connector |
|---|---|---|
| `19.0` | 19 and later | `odoo` (JSON-2 API) |
| `18.0` | 18 | `odoo-jsonrpc` |
| `17.0` | 17 | `odoo-jsonrpc` |

`17.0` and `18.0` contain Python and run on Odoo.sh and on-premise only (Odoo Online always
runs the latest version). Without the module you can enter the same values by hand, see the
[Odoo guide](https://anythingmcp.com/guides/connect-odoo-to-claude).

## Self-hosted AnythingMCP

AnythingMCP is open source ([HelpCode-ai/anythingmcp](https://github.com/HelpCode-ai/anythingmcp)).
To use your own instance, set the system parameter `anythingmcp_connector.url` to its address,
e.g. `https://mcp.example.com`. The default is `https://cloud.anythingmcp.com`.

## Tests

`tools/run-test.sh 19.0` starts a throwaway Odoo and Postgres (Docker) and checks the module
twice: imported as a zip through *Import Module*, as on Odoo Online, and installed from the
addons path. `tools/check_module.py` signs in over Odoo's web API, runs both buttons' server
actions and checks the link and the API key dialog.

## License

LGPL-3.0. Made by helpcode.ai GmbH, Freiburg, Germany. Support: support@anythingmcp.com
