# AnythingMCP for Odoo

Use Odoo in Claude, ChatGPT and Copilot. This Odoo module adds an **AI Assistants** block to
*Settings → General Settings* that connects your Odoo to [AnythingMCP](https://anythingmcp.com)
in three steps:

1. **Create an API key** opens Odoo's own dialog for a new API key of your user.
2. **Open AnythingMCP** opens the AnythingMCP setup with your Odoo address, database name
   and (on Odoo 17 and 18) user id already filled in. You paste the key there; it is never
   part of the link.
3. AnythingMCP checks the key against your Odoo, then shows how to add it to your assistant.

The module adds no models, stores nothing and calls no external service by itself.

| Branch | Odoo | AnythingMCP connector |
|---|---|---|
| `19.0` | 19 and later | `odoo` (JSON-2 API) |
| `18.0` | 18 | `odoo-jsonrpc` |
| `17.0` | 17 | `odoo-jsonrpc` |

Odoo Online cannot install third-party modules; there you enter the same values by hand,
see the [Odoo guide](https://anythingmcp.com/guides/connect-odoo-to-claude).

## Self-hosted AnythingMCP

AnythingMCP is open source ([HelpCode-ai/anythingmcp](https://github.com/HelpCode-ai/anythingmcp)).
To use your own instance, set the system parameter `anythingmcp_connector.url` to its address,
e.g. `https://mcp.example.com`. The default is `https://cloud.anythingmcp.com`.

## Tests

`tools/run-test.sh 19.0` installs the module in a throwaway Odoo and Postgres (Docker) and runs
its tests. Use the branch's Odoo version.

## License

LGPL-3.0. Made by helpcode.ai GmbH, Freiburg, Germany. Support: support@anythingmcp.com
