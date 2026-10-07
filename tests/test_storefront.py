"""Exercise the actual storefront JavaScript against independent API failures."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "frontend" / "index.html").read_text()
SCRIPT = re.search(r"<script>(.*?)</script>", HTML, re.S).group(1)
NODE = r'''
const vm=require("node:vm"),fs=require("node:fs");
const input=JSON.parse(fs.readFileSync(0,"utf8")),panels={},calls=[];
const context=vm.createContext({
  document:{getElementById(id){return panels[id]??=( {innerHTML:"",textContent:"",value:"",disabled:false,
    setAttribute(name,value){this[name]=value}})}},
  async fetch(path){calls.push(path);const item=input.responses[path]||{ok:false,data:{}};
    return {ok:item.ok,json:async()=>item.data}}
});
vm.runInContext(input.script,context);
(async()=>{
  await vm.runInContext("Promise.all([refreshLegacy(),loadProducts(),refreshStatus()])",context);
  const first=JSON.parse(JSON.stringify(panels));
  if(input.retry){Object.assign(input.responses,input.retry);await vm.runInContext("refreshLegacy()",context)}
  process.stdout.write(JSON.stringify({first,panels,calls}));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1});
'''


@unittest.skipUnless(shutil.which("node"), "Node.js is required for storefront functional tests")
class StorefrontTests(unittest.TestCase):
    def render(self, overrides=None, retry=None):
        responses = {
            "/api/orders": {"ok": True, "data": {"orders": [{"order_id": "ORD-1001", "status": "Processing"}]}},
            "/api/account": {"ok": True, "data": {"customer": {"name": "Demo Customer", "status": "Active"}}},
        }
        responses.update(overrides or {})
        result = subprocess.run(["node", "-e", NODE], input=json.dumps({"script": SCRIPT, "responses": responses,
                                                                         "retry": retry}), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_legacy_data_renders_even_when_catalogue_is_unavailable(self):
        result = self.render()
        self.assertIn("ORD-1001", result["panels"]["ordersBody"]["innerHTML"])
        self.assertIn("Processing", result["panels"]["ordersBody"]["innerHTML"])
        self.assertIn("Demo Customer", result["panels"]["accountBody"]["innerHTML"])
        self.assertIn("Active", result["panels"]["accountBody"]["innerHTML"])
        self.assertIn("Catalogue is not available", result["panels"]["productGrid"]["innerHTML"])
        self.assertIn("Legacy system", HTML)
        self.assertIn("Additional feature", HTML)

    def test_failed_orders_do_not_hide_account_and_refresh_recovers(self):
        result = self.render({"/api/orders": {"ok": False, "data": {"error": "database_unavailable"}}},
                             retry={"/api/orders": {"ok": True, "data": {"orders": [{"order_id": "ORD-1002", "status": "Ready"}]}}})
        self.assertIn("temporarily unavailable", result["first"]["ordersBody"]["innerHTML"])
        self.assertIn("Demo Customer", result["first"]["accountBody"]["innerHTML"])
        self.assertIn("ORD-1002", result["panels"]["ordersBody"]["innerHTML"])
        self.assertFalse(result["panels"]["legacyRefresh"]["disabled"])
        self.assertEqual(result["panels"]["ordersBody"]["aria-busy"], "false")

    def test_failed_account_does_not_hide_orders(self):
        result = self.render({"/api/account": {"ok": False, "data": {}}})
        self.assertIn("temporarily unavailable", result["panels"]["accountBody"]["innerHTML"])
        self.assertIn("ORD-1001", result["panels"]["ordersBody"]["innerHTML"])

    def test_invalid_http_200_payloads_show_errors_instead_of_fake_records(self):
        result = self.render({"/api/orders": {"ok": True, "data": {"orders": [{"status": "Ready"}]}},
                              "/api/account": {"ok": True, "data": {"customer": {}}}})
        self.assertIn("temporarily unavailable", result["panels"]["ordersBody"]["innerHTML"])
        self.assertIn("temporarily unavailable", result["panels"]["accountBody"]["innerHTML"])
        self.assertNotIn("Demo Customer", result["panels"]["accountBody"]["innerHTML"])

    def test_api_text_is_escaped_and_empty_orders_have_an_explicit_state(self):
        result = self.render({"/api/orders": {"ok": True, "data": {"orders": []}},
                              "/api/account": {"ok": True, "data": {"customer": {"name": "<img onerror=bad>", "status": "Active"}}}})
        self.assertIn("No orders found", result["panels"]["ordersBody"]["innerHTML"])
        account = result["panels"]["accountBody"]["innerHTML"]
        self.assertIn("&lt;img onerror=bad&gt;", account)
        self.assertNotIn("<img", account)
