from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from odoo.release import version_info
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAnythingMcpSettings(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env["ir.config_parameter"].sudo().set_param("web.base.url", "https://acme.example.com/")
        self.settings = self.env["res.config.settings"].create({})

    def test_values_shown(self):
        self.assertEqual(self.settings.anythingmcp_odoo_url, "https://acme.example.com")
        self.assertEqual(self.settings.anythingmcp_database, self.env.cr.dbname)
        self.assertEqual(self.settings.anythingmcp_user_id, self.env.uid)

    def test_setup_link_carries_no_key(self):
        action = self.settings.action_anythingmcp_open_setup()
        self.assertEqual(action["type"], "ir.actions.act_url")
        url = urlparse(action["url"])
        query = parse_qs(url.query)
        self.assertEqual(url.netloc, "cloud.anythingmcp.com")
        self.assertEqual(query["prefill.ODOO_URL"], ["https://acme.example.com"])
        self.assertEqual(query["prefill.ODOO_DB"], [self.env.cr.dbname])
        self.assertFalse(any("KEY" in name for name in query))
        if version_info[0] >= 19:
            self.assertEqual(url.path, "/connectors/setup/odoo")
            self.assertNotIn("prefill.ODOO_UID", query)
        else:
            self.assertEqual(url.path, "/connectors/setup/odoo-jsonrpc")
            self.assertEqual(query["prefill.ODOO_UID"], [str(self.env.uid)])

    def test_self_hosted_instance(self):
        self.env["ir.config_parameter"].sudo().set_param("anythingmcp_connector.url", "https://mcp.acme.example/")
        url = urlparse(self.settings.action_anythingmcp_open_setup()["url"])
        self.assertEqual(url.netloc, "mcp.acme.example")

    def test_api_key_dialog(self):
        # Odoo's own dialog, behind its password check (which needs a browser
        # request, so the call itself is stubbed here).
        users = type(self.env.user)
        with patch.object(users, "api_key_wizard", autospec=True, return_value={"type": "ir.actions.act_window"}) as wizard:
            action = self.settings.action_anythingmcp_new_api_key()
        self.assertEqual(action, {"type": "ir.actions.act_window"})
        self.assertEqual(wizard.call_args.args[0], self.env.user)
