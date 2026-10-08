#!/usr/bin/env python3
"""Build a Linux/x86_64 Python 3.12 Lambda ZIP and upload an immutable content key."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from lab_support import aws_json

ROOT = Path(__file__).resolve().parents[1]


def package(bucket):
    with tempfile.TemporaryDirectory(prefix="anygroup-rotation-") as temporary:
        directory = Path(temporary)
        target = directory / "function"
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-compile",
            "--target", str(target), "--only-binary=:all:", "--implementation", "cp",
            "--python-version", "3.12", "--abi", "cp312", "--abi", "abi3", "--abi", "none",
            "--platform", "manylinux_2_34_x86_64", "--platform", "manylinux_2_28_x86_64",
            "--platform", "manylinux2014_x86_64", "-r", str(ROOT / "rotation-service/requirements.txt")
        ], check=True, stdout=sys.stderr)
        (target / "app.py").write_bytes((ROOT / "rotation-service/app.py").read_bytes())
        archive = directory / "rotation.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
            for path in sorted(target.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(target).as_posix(), (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o644 << 16
                    output.writestr(info, path.read_bytes())
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        key = f"rotation/{digest}.zip"
        aws_json("s3api", "put-object", "--bucket", bucket, "--key", key,
                 "--body", str(archive), "--server-side-encryption", "AES256")
        return key


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", required=True)
    print(package(parser.parse_args().bucket))
