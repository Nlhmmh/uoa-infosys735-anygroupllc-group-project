import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SetupTests(unittest.TestCase):
    def run_setup(self, failing=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts, bin_dir = root / "scripts", root / "bin"
            scripts.mkdir(); bin_dir.mkdir()
            shutil.copy(ROOT / "scripts" / "lab.sh", scripts / "lab.sh")
            log = root / "calls"
            stub = '#!/bin/bash\nset -eu\nprintf "%s %s\\n" "$(basename "$0")" "$*" >> "$CALL_LOG"\nif [[ "$(basename "$0")" == "$FAIL_STEP" && "${1:-}" == "foundation" ]]; then exit 1; fi\n'
            for name in ("part13_deploy_all.sh", "part12_build_push.sh", "part12_seed_catalogue.sh", "part12_test_catalogue.sh"):
                (scripts / name).write_text(stub)
                (scripts / name).chmod(0o755)
            for name in ("part15_seed_database.py", "part14_collect_evidence.py"):
                (scripts / name).write_text('import os\nfrom pathlib import Path\nwith open(os.environ["CALL_LOG"],"a") as f: f.write(Path(__file__).name+"\\n")\n')
            (bin_dir / "docker").write_text('#!/bin/bash\nexit 0\n')
            (bin_dir / "docker").chmod(0o755)
            (bin_dir / "aws").write_text('''#!/usr/bin/env python3
import os,sys
a=sys.argv[1:]
with open(os.environ["CALL_LOG"],"a") as f: f.write("aws "+" ".join(a[:2])+"\\n")
if a[:2]==["cloudformation","describe-stacks"]: print("test-resource")
elif a[:2]==["ecr","describe-images"]:
 print("ImageNotFoundException",file=sys.stderr);sys.exit(255)
elif a[:2]==["s3","cp"]: pass
else: sys.exit("Unexpected stub operation")
''')
            (bin_dir / "aws").chmod(0o755)
            env = {**os.environ, "PATH": str(bin_dir)+os.pathsep+os.environ["PATH"],
                   "CALL_LOG": str(log), "FAIL_STEP": failing, "EVIDENCE_DIR": str(root / "evidence")}
            result = subprocess.run(["bash", str(scripts / "lab.sh"), "setup", "test@example.invalid", "v1"],
                                    env=env, capture_output=True, text=True)
            return result, log.read_text().splitlines()

    def test_setup_runs_all_phases_and_checks_in_dependency_order(self):
        result, calls = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        stages = [c for c in calls if not c.startswith("aws")]
        self.assertEqual([c.split()[0] for c in stages], [
            "part13_deploy_all.sh", "part13_deploy_all.sh", "part12_build_push.sh", "part12_seed_catalogue.sh",
            "part15_seed_database.py", "part13_deploy_all.sh", "part12_test_catalogue.sh", "part14_collect_evidence.py"])
        self.assertEqual(sum(c == "aws s3 cp" for c in calls), 3)
        self.assertIn("foundation test@example.invalid", stages[1])
        self.assertIn("feature v1", stages[5])

    def test_failed_foundation_stops_before_images_seeding_or_feature_activation(self):
        result, calls = self.run_setup("part13_deploy_all.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any("foundation" in c for c in calls))
        self.assertFalse(any("seed" in c or "feature" in c or "s3 cp" in c for c in calls))


class FailoverEvidenceTests(unittest.TestCase):
    def test_failover_requires_changed_az_same_endpoint_and_preserved_rows(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from part15_test_rds_failover import restored
        before = {"AvailabilityZone": "zone-a", "Endpoint": {"Address": "stable-db"}}
        after = {"DBInstanceStatus": "available", "MultiAZ": True, "AvailabilityZone": "zone-b", "Endpoint": {"Address": "stable-db"}}
        rows = [{"order_id": "ORD-1001"}]
        self.assertTrue(restored(before, after, rows, rows))
        self.assertFalse(restored(before, {**after, "AvailabilityZone": "zone-a"}, rows, rows))
        self.assertFalse(restored(before, {**after, "Endpoint": {"Address": "another-db"}}, rows, rows))
        self.assertFalse(restored(before, after, rows, []))
        self.assertFalse(restored(before, {k: v for k, v in after.items() if k != "AvailabilityZone"}, rows, rows))
