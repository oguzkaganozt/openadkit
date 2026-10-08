"""Integrator evidence binds the source overlay and checks every hook report."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from release_fixtures import RELEASE_SHA, build_metadata

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".github/scripts"
sys.path.insert(0, str(SCRIPTS))

import validation_matrix  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / "evidence" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conformance = load("overlay_conformance")
subjects = load("subjects")


def test_example_evidence_cells_follow_the_base_distros():
    runtime = validation_matrix.load_runtime(ROOT)
    assert validation_matrix.example_kit_cells(runtime, ROOT) == [
        {"deployment": "custom-kit", "distro": distro, "kit": "deployments/custom-kit"}
        for distro in ("humble", "jazzy")
    ]


def test_old_source_layout_keeps_its_original_cells_and_overlay_subject(tmp_path):
    for directory in ("cli", "deployments"):
        shutil.copytree(ROOT / directory, tmp_path / directory, ignore=shutil.ignore_patterns("__pycache__", "custom-kit"))
    shutil.copy2(ROOT / "openadkit.json", tmp_path / "openadkit.json")
    legacy = tmp_path / "examples/custom-kit"
    deployment = legacy / "deployments/custom-planning"
    shutil.copytree(ROOT / "deployments/custom-kit", deployment)
    document = json.loads((deployment / "openadkit.json").read_text())
    document["deployments"] = {"custom-planning": {"path": "deployments/custom-planning"}}
    (legacy / "openadkit.json").write_text(json.dumps(document))
    (deployment / "openadkit.json").unlink()
    manifest = json.loads((deployment / "deployment.json").read_text())
    manifest["name"] = "custom-planning"
    (deployment / "deployment.json").write_text(json.dumps(manifest))
    runtime = validation_matrix.load_runtime(tmp_path)
    assert validation_matrix.example_kit_cells(runtime, tmp_path) == [
        {"deployment": "custom-planning", "distro": distro, "kit": "examples/custom-kit"} for distro in ("humble", "jazzy")]
    expected = runtime.deployment_checksum(legacy, exclude_dirs=("build", "install", "log"))
    assert (expected, "overlay:examples/custom-kit") in subjects.build_subjects({}, tmp_path)


def test_staged_flat_example_inherits_pins_without_host_build_products(tmp_path):
    source = tmp_path / "source"
    for directory in ("cli", "deployments", ".github/scripts"):
        shutil.copytree(ROOT / directory, source / directory, ignore=shutil.ignore_patterns("__pycache__", "build", "install", "log"))
    for file in ("openadkit", "openadkit.json"):
        shutil.copy2(ROOT / file, source / file)
    workspace = source / "deployments/custom-kit/overlay_ws"
    for product in ("build", "install", "log"):
        (workspace / product).mkdir()
        (workspace / product / "host-product").write_text("not evidence")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps(build_metadata()))
    staged = tmp_path / "staged"
    result = subprocess.run(["bash", str(source / ".github/scripts/evidence/stage_kit.sh"), str(source), str(metadata), str(staged), RELEASE_SHA],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    runtime = validation_matrix.load_runtime(staged)
    example = staged / "deployments/custom-kit"
    kit = runtime.load_kit(example)
    assert set(kit.deployments) == {"custom-kit"} and kit.deployments["custom-kit"].path == "."
    assert all("@sha256:" in ref for refs in kit.images.values() for ref in refs.values())
    assert (example / "overlay_ws/src/acme_probe/src/probe.cpp").is_file()
    assert not any((example / "overlay_ws" / product).exists() for product in ("build", "install", "log"))
    assert not (staged / "examples").exists()


def test_overlay_subject_ignores_build_products_but_binds_sources(tmp_path):
    tree = tmp_path / "source"
    for directory in ("cli", "deployments"):
        shutil.copytree(ROOT / directory, tree / directory, ignore=shutil.ignore_patterns("__pycache__", "build", "install", "log"))
    shutil.copy2(ROOT / "openadkit.json", tree / "openadkit.json")
    kit = tree / "deployments/custom-kit"

    def digest():
        return dict((name, digest) for digest, name in subjects.build_subjects({}, tree))["overlay:deployments/custom-kit"]

    initial = digest()
    generated = kit / "overlay_ws/install"
    generated.mkdir()
    (generated / "host-binary").write_bytes(b"binary")
    assert digest() == initial
    (kit / "config.env").write_text("VEHICLE_ID=changed\n")
    assert digest() != initial


@pytest.mark.parametrize("report, expected", [
    (json.dumps({"unknownPackages": [], "unknownFiles": [], "unknownKeys": []}), True),
    (json.dumps({"unknownPackages": [], "unknownFiles": [], "unknownKeys": ["typo"]}), False),
    ("", False),
    ("[]", False),
    (json.dumps({"unknownPackages": [], "unknownFiles": [], "unknownKeys": "bad"}), False),
])
def test_hook_reports_are_required_and_unknown_keys_are_nonconformant(report, expected):
    containers = [
        {"Id": "hooked", "Name": "/control", "Mounts": [{"Destination": "/openadkit/config/deployment"}]},
        {"Id": "external", "Name": "/heartbeat", "Mounts": []},
    ]
    reports = conformance.collect_reports(containers, lambda id: report)
    assert len(reports) == 1
    assert reports[0]["container"] == "control"
    assert reports[0]["conformant"] is expected


def test_test_result_preserves_overlay_conformance(tmp_path):
    cells = tmp_path / "cells"
    cells.mkdir()
    (cells / "cell.json").write_text(json.dumps({
        "name": "custom-kit-humble-linux-amd64", "deployment": "custom-kit",
        "distro": "humble", "result": "PASSED", "overlayConformant": False,
        "levels": {"L0": {"ok": True}, "L1": {"ok": True}, "L2": {"ok": True}},
    }))
    metadata = tmp_path / "metadata.json"
    metadata.write_text('{}')
    output = tmp_path / "attestation"
    result = subprocess.run([
        sys.executable, str(SCRIPTS / "evidence/test_result.py"), "--cells-dir", str(cells),
        "--build-metadata", str(metadata), "--source-root", str(ROOT), "--output-dir", str(output),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    predicate = json.loads((output / "evidence-predicate.json").read_text())
    assert predicate["configuration"][0]["annotations"]["openadkitCell"]["overlayConformant"] is False
    assert json.loads((output / "evidence-summary.json").read_text())["cells"][0]["overlayConformant"] is False
