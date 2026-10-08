#!/usr/bin/env python3
"""Build the lab ZIP from an explicit source allowlist, excluding live evidence and credentials."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def build():
    files = []
    for folder, extensions in (("cloudformation", {".yaml", ".json", ".csv"}), ("sample-images", {".jpg"}),
                               ("scripts", {".py", ".sh"}), ("tests", {".py"})):
        files.extend(p for p in (ROOT / folder).glob("*") if p.is_file() and p.suffix in extensions and not p.name.startswith("."))
    files.extend(ROOT / "data" / name for name in ("part11_sample_catalogue_keys.json", "part12_catalogue_seed.json",
        "part13_stack_manifest.json", "part13_static_validation_report.json", "cost_model_inputs.json", "lab_evidence_review.json"))
    files.extend(ROOT / "catalogue-service" / name for name in ("app.py", "Dockerfile", "requirements.txt", "README.md", ".dockerignore"))
    files.extend(ROOT / "backend-service" / name for name in ("app.py", "requirements.txt"))
    files.extend(ROOT / "rotation-service" / name for name in ("app.py", "requirements.txt"))
    files.append(ROOT / "frontend" / "index.html")
    files.extend(ROOT / name for name in ("README.md", "instructions.md", "AnyGroupLLC_case_study.md",
        "IaC_Deployment_and_Usage_Instructions.md", "Presentation_and_Slide_Content.md", "Rubric_and_Assessment_Checklist.md", "requirements-validation.txt", "part13_iac_evidence_checklist.csv"))
    archive = ROOT / "anygroup-gp2-deployment.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(set(files)):
            output.write(path, path.relative_to(ROOT).as_posix())
    return archive, len(set(files))


if __name__ == "__main__":
    archive, count = build()
    print(f"Packaged {count} source files into {archive.name}.")
