from urllib.parse import urlencode

from odoo import fields, models
from odoo.release import version_info

# AnythingMCP Cloud. Self-hosted AnythingMCP users can point the module at
# their own instance with the system parameter below.
DEFAULT_ANYTHINGMCP_URL = "https://cloud.anythingmcp.com"
ANYTHINGMCP_URL_PARAM = "anythingmcp_connector.url"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Defaults rather than computed fields: the settings form is a new record,
    # and these values only describe this database and the signed-in user.
    anythingmcp_odoo_url = fields.Char(string="Odoo address", readonly=True, default=lambda self: self._anythingmcp_odoo_url())
    anythingmcp_database = fields.Char(string="Database name", readonly=True, default=lambda self: self.env.cr.dbname)
    anythingmcp_user_id = fields.Integer(string="User ID", readonly=True, default=lambda self: self.env.uid)
    anythingmcp_needs_user_id = fields.Boolean(readonly=True, default=lambda self: self._anythingmcp_connector() == "odoo-jsonrpc")

    def _anythingmcp_odoo_url(self):
        return (self.env["ir.config_parameter"].sudo().get_param("web.base.url") or "").rstrip("/")

    def _anythingmcp_connector(self):
        # Odoo 19 and newer have the JSON-2 API; older versions use JSON-RPC,
        # which also needs the user id. AnythingMCP has one connector for each.
        return "odoo" if version_info[0] >= 19 else "odoo-jsonrpc"

    def action_anythingmcp_new_api_key(self):
        """Open Odoo's own dialog for a new API key of the current user."""
        return self.env.user.api_key_wizard()

    def action_anythingmcp_open_setup(self):
        """Open the AnythingMCP setup with the address, database and user id filled in.

        Only these three values go into the link. The API key is never part of
        it: the user pastes it on the AnythingMCP page.
        """
        self.ensure_one()
        connector = self._anythingmcp_connector()
        # Read again rather than from the form: the record's values are only
        # what was shown when the page opened.
        values = {
            "prefill.ODOO_URL": self._anythingmcp_odoo_url(),
            "prefill.ODOO_DB": self.env.cr.dbname,
        }
        if connector == "odoo-jsonrpc":
            values["prefill.ODOO_UID"] = str(self.env.uid)
        base = self.env["ir.config_parameter"].sudo().get_param(ANYTHINGMCP_URL_PARAM) or DEFAULT_ANYTHINGMCP_URL
        return {
            "type": "ir.actions.act_url",
            "url": f"{base.rstrip('/')}/connectors/setup/{connector}?{urlencode(values)}",
            "target": "new",
        }
