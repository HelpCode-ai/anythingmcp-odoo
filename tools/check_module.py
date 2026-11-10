"""Checks the installed module over Odoo's web API, as a browser would use it.

usage: python3 tools/check_module.py <odoo url> <database> [<module zip to import first>]
Signs in as admin/admin, optionally imports the zip the way Apps > Import
Module does, runs both buttons' server actions and checks what they return.
Exits non-zero on a failure.
"""
import base64
import http.cookiejar
import json
import sys
import urllib.parse
import urllib.request

URL, DB = sys.argv[1].rstrip("/"), sys.argv[2]
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def rpc(path, params):
    body = json.dumps({"jsonrpc": "2.0", "method": "call", "params": params}).encode()
    request = urllib.request.Request(URL + path, body, {"Content-Type": "application/json"})
    reply = json.load(opener.open(request))
    if "error" in reply:
        raise SystemExit(f"FAIL {path}: {reply['error']['data']['message']}")
    return reply["result"]


def call(model, method, *args, **kwargs):
    return rpc(f"/web/dataset/call_kw/{model}/{method}", {"model": model, "method": method, "args": list(args), "kwargs": kwargs})


def check(condition, message):
    print(("ok   " if condition else "FAIL ") + message)
    if not condition:
        raise SystemExit(1)


rpc("/web/session/authenticate", {"db": DB, "login": "admin", "password": "admin"})

if len(sys.argv) > 3:
    with open(sys.argv[3], "rb") as zipped:
        wizard = call("base.import.module", "create", {"module_file": base64.b64encode(zipped.read()).decode()})
    call("base.import.module", "import_module", [wizard])

module = call("ir.module.module", "search_read", [["name", "=", "anythingmcp_connector"]], fields=["state", "latest_version", "imported"])
check(module and module[0]["state"] == "installed", f"module installed {module}")

call("ir.config_parameter", "set_param", "web.base.url", "https://acme.example.com/")
settings = call("res.config.settings", "create", {})
actions = {
    row["name"]: row["res_id"]
    for row in call("ir.model.data", "search_read", [["module", "=", "anythingmcp_connector"], ["model", "=", "ir.actions.server"]], fields=["name", "res_id"])
}
context = {"active_model": "res.config.settings", "active_id": settings, "active_ids": [settings]}

arch = call("res.config.settings", "get_views", [[False, "form"]])["views"]["form"]["arch"]
check("AI Assistants" in arch, "settings show the AI Assistants block")
for name in ("action_new_api_key", "action_open_setup"):
    check(f'name="{actions[name]}"' in arch, f"a button runs {name}")

action = rpc("/web/action/run", {"action_id": actions["action_open_setup"], "context": context})
url = urllib.parse.urlparse(action["url"])
query = urllib.parse.parse_qs(url.query)
check(action["type"] == "ir.actions.act_url" and action["target"] == "new", "Open AnythingMCP opens a new tab")
check(url.netloc == "cloud.anythingmcp.com" and url.path == "/connectors/setup/odoo", f"link goes to the odoo connector ({url.netloc}{url.path})")
check(query == {"prefill.ODOO_URL": ["https://acme.example.com"], "prefill.ODOO_DB": [DB], "source": ["odoo_module"]}, f"link carries address, database and source only {query}")

# Characters that need encoding survive the hand-made encoding.
call("ir.config_parameter", "set_param", "web.base.url", "https://acme.example.com:8443/odoo?x=1&y=ü")
query = urllib.parse.parse_qs(urllib.parse.urlparse(rpc("/web/action/run", {"action_id": actions["action_open_setup"], "context": context})["url"]).query)
check(query["prefill.ODOO_URL"] == ["https://acme.example.com:8443/odoo?x=1&y=ü"], f"address with special characters is encoded {query['prefill.ODOO_URL']}")

call("ir.config_parameter", "set_param", "anythingmcp_connector.url", "https://mcp.acme.example/")
action = rpc("/web/action/run", {"action_id": actions["action_open_setup"], "context": context})
check(action["url"].startswith("https://mcp.acme.example/connectors/setup/odoo?"), "self-hosted address is used")

action = rpc("/web/action/run", {"action_id": actions["action_new_api_key"], "context": context})
check(action["type"] == "ir.actions.act_window" and action["res_model"] == "res.users.identitycheck", f"Create an API key asks for the password first ({action.get('res_model')})")

if call("res.lang", "search_count", [["code", "=", "it_IT"]]):
    arch = call("res.config.settings", "get_views", [[False, "form"]], context={"lang": "it_IT"})["views"]["form"]["arch"]
    check("Assistenti IA" in arch and "Apri AnythingMCP" in arch, "Italian translation loaded")
print("all checks passed")
