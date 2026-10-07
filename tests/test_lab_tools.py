import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import part14_collect_evidence as collector
import part14_probe_availability as probe
import part12_test_catalogue as smoke

AWS_STUB = '''#!/usr/bin/env python3
import json,os,sys
a=sys.argv[1:]
with open(os.environ["STUB_LOG"],"a") as out: out.write(json.dumps(a)+"\\n")
def value(flag): return a[a.index(flag)+1] if flag in a else ""
if os.getenv("STUB_DENY"):
 print("An error occurred (AccessDenied) when calling DescribeStacks",file=sys.stderr);sys.exit(255)
if a[:2]==["sts","get-caller-identity"]: print('{"Account":"000000000000","Arn":"test"}')
elif a[:2]==["ec2","describe-instances"]: print(os.getenv("STUB_COUNT","4") if "length(Reservations[].Instances[])"==value("--query") else "0")
elif a[:2]==["rds","describe-orderable-db-instance-options"]:
 print(json.dumps({"OrderableDBInstanceOptions": [] if os.getenv("STUB_NO_RDS") else [{"MultiAZCapable":True,"Vpc":True,"StorageType":"gp2","EngineVersion":"19.0.0.0.ru-2026-07.rur-2026-07.r1","MinStorageSize":20}]}))
elif a[:2]==["cloudformation","describe-stacks"]:
 q=value("--query")
 if q=="Stacks[0].Parameters":
  if os.getenv("STUB_ACTIVE"):
   print(json.dumps([{"ParameterKey":"DeployService","ParameterValue":"true"},{"ParameterKey":"ContainerImageTag","ParameterValue":"v1"},{"ParameterKey":"ContainerImageDigest","ParameterValue":"" if os.getenv("STUB_UNPINNED") else "sha256:"+"1"*64}]))
  else:
   print("An error occurred (ValidationError): Stack does not exist",file=sys.stderr);sys.exit(255)
 elif "EcrRepositoryName" in q: print("anygroup-gp2-catalogue")
 elif "CatalogueTableName" in q: print("anygroup-gp2-catalogue")
 elif "CatalogueImageBucketName" in q: print("test-images")
 else: print("CREATE_COMPLETE")
elif a[:2]==["ecr","describe-images"]: print("sha256:"+"1"*64)
elif a[:2]==["dynamodb","get-item"]: print("None" if os.getenv("STUB_MISSING_SEED") else json.loads(value("--key"))["product_id"]["S"])
elif a[:2] in (["cloudformation","deploy"],["s3api","head-object"]): print("{}")
else: raise SystemExit("Unexpected AWS stub operation: "+str(a))
'''


class DeploymentTests(unittest.TestCase):
    def run_script(self, name, args, **settings):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory)/"aws"
            stub.write_text(AWS_STUB)
            stub.chmod(0o755)
            log = Path(directory)/"calls.jsonl"
            env = {**os.environ, "PATH": directory + os.pathsep + os.environ["PATH"], "STUB_LOG": str(log), **settings}
            result = subprocess.run(["bash", str(ROOT/"scripts"/name), *args], env=env, capture_output=True, text=True)
            calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            return result, calls

    def test_feature_pins_verified_digest_and_checks_seed_images(self):
        result, calls = self.run_script("part13_deploy_all.sh", ["feature", "v2"])
        self.assertEqual(result.returncode, 0, result.stderr)
        deploy = next(c for c in calls if c[:2] == ["cloudformation", "deploy"])
        self.assertIn("ContainerImageDigest=sha256:" + "1"*64, deploy)
        self.assertIn("ContainerImageTag=v2", deploy)
        self.assertEqual(sum(c[:2] == ["s3api", "head-object"] for c in calls), 3)

    def test_peak_ec2_count_blocks_deployment_before_mutation(self):
        result, calls = self.run_script("part13_deploy_all.sh", ["foundation"], STUB_COUNT="9")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(c[:2] == ["cloudformation", "deploy"] for c in calls))

    def test_unsupported_oracle_multi_az_blocks_before_charged_resources(self):
        result, calls = self.run_script("part13_deploy_all.sh", ["foundation"], STUB_NO_RDS="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(c[:2] == ["cloudformation", "deploy"] for c in calls))
        self.assertIn("No orderable Oracle", result.stderr)

    def test_foundation_preserves_active_service_parameters(self):
        result, calls = self.run_script("part13_deploy_all.sh", ["foundation"], STUB_ACTIVE="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        micro = next(c for c in calls if c[:2] == ["cloudformation", "deploy"] and "anygroup-gp2-microservice" in c)
        self.assertNotIn("DeployService=false", micro)
        self.assertFalse(any(c.startswith("ContainerImageTag=") for c in micro))

    def test_status_does_not_disguise_access_denial_as_missing_stack(self):
        result, _ = self.run_script("part13_deploy_all.sh", ["status"], STUB_DENY="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("NOT_FOUND", result.stdout)
        self.assertIn("AccessDenied", result.stderr)

    def test_existing_unpinned_catalogue_upgrades_without_deactivation(self):
        result, calls = self.run_script("part13_deploy_all.sh", ["foundation"], STUB_ACTIVE="1", STUB_UNPINNED="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        micro = next(c for c in calls if c[:2] == ["cloudformation", "deploy"] and "anygroup-gp2-microservice" in c)
        self.assertIn("DeployService=true", micro)
        self.assertIn("ContainerImageDigest=sha256:" + "1"*64, micro)

    def test_missing_seed_blocks_activation(self):
        result, calls = self.run_script("part13_deploy_all.sh", ["feature"], STUB_MISSING_SEED="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(c[:2] == ["cloudformation", "deploy"] for c in calls))

    def test_teardown_stops_on_access_denial(self):
        result, calls = self.run_script("part13_teardown_all.sh", ["--yes"], STUB_DENY="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(c[:2] == ["cloudformation", "delete-stack"] for c in calls))


class EvidenceTests(unittest.TestCase):
    def test_failed_reads_do_not_produce_security_pass(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(collector, "aws_json", side_effect=RuntimeError("AccessDenied")), \
             patch.object(collector, "stack_outputs", side_effect=RuntimeError("AccessDenied")):
            result = collector.collect(Path(directory))
            self.assertEqual(result["status"], "PARTIAL")
            self.assertFalse(result["security_configuration_checks"]["configuration_complete"])
            self.assertIsNone(result["actual_cost"])

    def test_failed_teardown_reads_cannot_claim_no_orphans(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(collector, "aws_json", side_effect=RuntimeError("AccessDenied")):
            self.assertEqual(collector.collect(Path(directory), True)["status"], "PARTIAL")

    def test_known_managed_secret_not_found_counts_as_removed(self):
        def reads(*args):
            if args[:2] == ("secretsmanager", "describe-secret"):
                raise RuntimeError("ResourceNotFoundException")
            return {}
        with tempfile.TemporaryDirectory() as directory, patch.object(collector, "aws_json", side_effect=reads):
            result = collector.collect(Path(directory), True, "known-rds-secret-arn")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["remaining_resource_counts"]["known_rds_managed_secret"], 0)

    def test_probe_summary_preserves_failures_and_latency(self):
        data = [{"http_status": 200, "functional_success": True, "latency_ms": 20},
                {"http_status": 503, "functional_success": False, "latency_ms": 30},
                {"http_status": 200, "functional_success": True, "latency_ms": 40}]
        result = probe.summary(data)
        self.assertEqual(result["successes"], 2)
        self.assertEqual(result["observed_success_percent"], 66.67)
        self.assertEqual(result["successful_latency_p95_ms"], 40)
        self.assertTrue(result["failure_observed"])
        self.assertTrue(result["final_sample_success"])

    def test_empty_probe_does_not_invent_latency_or_availability(self):
        result = probe.summary([])
        self.assertIsNone(result["observed_success_percent"])
        self.assertIsNone(result["successful_latency_p95_ms"])

    def test_probe_rejects_malformed_functional_response_despite_http_200(self):
        for body in (b"not json", b'{"other":"P1001"}'):
            response = MagicMock()
            response.__enter__.return_value = response
            response.getcode.return_value = 200
            response.read.return_value = body
            with patch.object(probe, "urlopen", return_value=response):
                result = probe.sample("http://example.invalid", 1, "product.product_id", "P1001")
            self.assertEqual(result["http_status"], 200)
            self.assertFalse(result["functional_success"])

    def test_probe_accepts_expected_functional_value(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.getcode.return_value = 200
        response.read.return_value = b'{"product":{"product_id":"P1001"}}'
        with patch.object(probe, "urlopen", return_value=response):
            self.assertTrue(probe.sample("http://example.invalid", 1, "product.product_id", "P1001")["functional_success"])


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.core = {"AlbDnsName": "example.invalid", "FrontendTargetGroupArn": "front",
                     "BackendTargetGroupArn": "back"}
        self.micro = {"CatalogueServiceName": "catalogue", "CatalogueClusterName": "cluster",
                      "CatalogueTargetGroupArn": "catalogue"}

    def test_disabled_service_is_rejected_before_http_requests(self):
        with patch.object(smoke, "stack_outputs", side_effect=[self.core, {}]), patch.object(smoke, "http_get") as get:
            with self.assertRaisesRegex(AssertionError, "not enabled"):
                smoke.run_checks()
            get.assert_not_called()

    def test_wait_mode_waits_for_service_and_all_target_groups(self):
        with patch.object(smoke, "stack_outputs", side_effect=[self.core, self.micro]), \
             patch.object(smoke, "aws_json", return_value={}) as aws, \
             patch.object(smoke, "http_get", return_value=b"bad page"):
            with self.assertRaisesRegex(AssertionError, "Storefront"):
                smoke.run_checks(True)
            self.assertEqual(aws.call_count, 4)
            self.assertEqual(aws.call_args_list[0].args[:3], ("ecs", "wait", "services-stable"))
            self.assertEqual([call.args[-1] for call in aws.call_args_list[1:]], ["front", "back", "catalogue"])

    def test_unresolved_frontend_metadata_fails_smoke(self):
        with patch.object(smoke, "stack_outputs", side_effect=[self.core, self.micro]), \
             patch.object(smoke, "http_get", return_value=b"AnyGroup Market Instance: ${!INSTANCE_ID}"):
            with self.assertRaisesRegex(AssertionError, "metadata missing"):
                smoke.run_checks()

    def test_old_dummy_database_response_cannot_pass_current_smoke(self):
        responses = [b'AnyGroup Market Instance: i-123abc Legacy system Additional feature id="ordersBody" id="accountBody"', {"instance_id": "i-123abc", "availability_zone": "zone-a"},
                     {"all_reachable": True, "databases": [{}, {}]}]
        with patch.object(smoke, "stack_outputs", side_effect=[self.core, self.micro]), \
             patch.object(smoke, "http_get", side_effect=responses):
            with self.assertRaisesRegex(AssertionError, "RDS Oracle SQL"):
                smoke.run_checks()

    def test_old_storefront_without_legacy_panels_is_rejected(self):
        with patch.object(smoke, "stack_outputs", side_effect=[self.core, self.micro]), \
             patch.object(smoke, "http_get", return_value=b"AnyGroup Market Instance: i-123abc"):
            with self.assertRaisesRegex(AssertionError, "legacy order/account panels"):
                smoke.run_checks()
