{
    "name": "AnythingMCP: Use Odoo in Claude and ChatGPT",
    "summary": "Ask Claude, ChatGPT or Copilot about your invoices, sales orders, customers and products. "
    "Connects Odoo to AI assistants over MCP in three steps, without code.",
    "version": "19.0.2.0.0",
    "category": "Productivity",
    "author": "helpcode.ai GmbH",
    "maintainer": "helpcode.ai GmbH",
    "website": "https://anythingmcp.com/marketplace/odoo",
    "support": "support@anythingmcp.com",
    "license": "LGPL-3",
    "depends": ["base_setup"],
    # A data module: no Python code, so Odoo Online can import it
    # (Apps > Import Module) as well as Odoo.sh and on-premise.
    "data": [
        "data/actions.xml",
        "views/res_config_settings_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
}
