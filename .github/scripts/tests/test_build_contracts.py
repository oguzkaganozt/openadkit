"""Build selection and real Compose topology boundaries, without running containers."""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "cli"), str(ROOT / ".github/scripts")]

import build as matrices  # noqa: E402
import compose  # noqa: E402
import manifest  # noqa: E402

INVENTORY = json.loads((ROOT / ".github/image-inventory.json").read_text())


def test_inventory_bake_and_runtime_catalog_agree():
    bake = (ROOT / "components/docker-bake.hcl").read_text()
    targets = {image["target"] for image in INVENTORY["images"]}
    assert set(re.findall(r'^target\s+"(?!_|docker-metadata-action-)([\w-]+)"', bake, re.M)) == targets
    assert set(re.findall(r'target\s+"docker-metadata-action-([\w-]+)"', bake)) == targets
    kit = json.loads((ROOT / "openadkit.json").read_text())
    assert set(kit["componentImages"].values()) == {image["target"] for image in INVENTORY["images"] if image["stage"] == "component"}
    resolved = matrices.build_matrices(INVENTORY)
    index = {(row["target"], row["ros-distro"]): row["arches"] for row in resolved["manifest_matrix"]["include"]}
    assert index[("planning-control", "humble")] == "amd64 arm64"
    assert index[("sensing-perception-cuda", "jazzy")] == "amd64"
    assert {row["target"] for row in resolved["carla_matrix"]["include"]} == {"carla-interface"}
    assert "simulator" in {row["target"] for row in resolved["component_matrix"]["include"]}


@pytest.mark.parametrize(("path", "expected", "flags"), [
    ("components/universe-common/Dockerfile", {image["target"] for image in INVENTORY["images"]}, {"use_local_common": True}),
    ("components/sensing-perception/Dockerfile.cuda", {"sensing-perception-cuda"}, {}),
    ("components/sensing-perception/scripts/build.sh", {"sensing-perception", "sensing-perception-cuda"}, {}),
    ("components/simulator/Dockerfile", {"carla-interface"}, {"use_local_simulator": True}),
    ("docs/index.md", set(), {}),
])
def test_changed_inputs_select_required_builds(path, expected, flags):
    plan = matrices.build_single_image_plan(INVENTORY, [path])
    assert set(plan["targets_json"]) == expected
    assert all(plan[name] is value for name, value in flags.items())


def test_invalid_build_inputs_fail_closed():
    for options, message in [
        ({"target_input": "missing"}, "Unknown Bake target"),
        ({"distro": "rolling"}, "Unsupported ROS distro"),
        ({"changed_files": ["components/new-component/Dockerfile"]}, "Unmapped component build input"),
    ]:
        with pytest.raises(ValueError, match=message):
            matrices.build_single_image_plan(INVENTORY, **options)


@pytest.mark.parametrize(("target", "publish", "local"), [
    ("universe-common", True, False), ("sensing-perception-cuda", True, False),
    ("carla-interface", True, False), ("api", False, False), ("carla-interface", False, True),
])
def test_shared_build_recipe_keeps_pins_provenance_and_local_graphs(target, publish, local):
    uri = "docker-image://example/base@sha256:" + "c" * 64
    prepared = {"build_tag": "123-1", "autoware_input_ref": "1.8.0", "autoware_ref_type": "tag",
                "autoware_ref": "a" * 40, "autoware_base_version": "1.8.0", "autoware_lock_sha256": "e" * 64,
                "upstream_images": json.dumps({"humble": {name: {"uri": uri} for name in ("core-devel", "base", "base-cuda-runtime", "base-cuda-devel")}}),
                "use_local_common": str(local).lower(), "use_local_simulator": str(local).lower(), "simulator_context": uri}
    if not local:
        prepared.update(devel_context=uri, runtime_context=uri)
    recipe, targets = matrices.bake_recipe(INVENTORY, prepared, target, "humble", "linux/amd64", publish=publish,
                                           shared_common=False, common_cached=local, owner="example", source_sha="b" * 40, run_id="123")
    row = recipe["target"][target]
    assert targets == (["universe-common-devel", "universe-common"] if publish and target == "universe-common" else [target])
    if publish:
        assert row["labels"]['"org.opencontainers.image.autoware-lock-sha256"'] == "e" * 64
        assert row["labels"]['"org.opencontainers.image.openadkit-sha"'] == "b" * 40
        assert row["cache-to"][0].endswith(",mode=max")
        assert (row["contexts"].get("autoware-base-cuda-devel") == uri) is (target == "sensing-perception-cuda")
    else:
        assert not row["labels"] and "cache-to" not in row
        assert ("universe-common" in row["contexts"]) is (not local)
        assert ("simulator" in row["contexts"]) is (target == "carla-interface" and not local)


@pytest.mark.parametrize("path", ["components/universe-common/Dockerfile", "components/sensing-perception/Dockerfile.cuda"])
def test_runtime_keeps_lock_security_refresh_and_overlay_hook(path):
    text = (ROOT / path).read_text()
    runtime = text.rsplit("\nFROM ", 1)[1]
    assert "bash /tmp/link-lock/align.sh" in text
    assert runtime.index("bash /tmp/link-lock/lock.sh verify") < runtime.index("bash /tmp/security-refresh.sh") < runtime.index("COPY components/overlay/")
    assert 'ENTRYPOINT ["/docker-entrypoint.sh", "/opt/openadkit/openadkit-hook.sh"]' in runtime


@pytest.fixture
def compose_context(tmp_path, monkeypatch):
    if shutil.which("docker") is None:
        pytest.skip("docker compose is required")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENADKIT_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("OPENADKIT_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("ZENOH_LISTEN", "tcp/127.0.0.1:7447")
    monkeypatch.setenv("ZENOH_PEER", "tcp/127.0.0.1:7447")
    monkeypatch.setenv("REMOTE_PASSWORD", "ci-validate")
    monkeypatch.delenv("OPENADKIT_KIT", raising=False)
    monkeypatch.delenv("OPENADKIT_DELEGATED", raising=False)
    return manifest.load_kit(ROOT)


@pytest.mark.parametrize(("name", "node", "present", "absent"), [
    ("scenario-simulation", None, {"scenario_simulator", "map"}, {"zenoh-bridge"}),
    ("scenario-simulation", "autoware", {"map", "zenoh-bridge"}, {"scenario_simulator"}),
    ("scenario-simulation", "scenario", {"scenario_simulator", "zenoh-bridge"}, {"map", "vehicle"}),
    ("carla-simulation", None, {"carla", "carla-interface", "map"}, {"zenoh-bridge"}),
    ("carla-simulation", "autoware", {"map", "zenoh-bridge"}, {"carla", "carla-interface"}),
    ("carla-simulation", "carla", {"carla", "carla-interface", "carla-map-loader", "zenoh-bridge"}, {"map", "vehicle"}),
])
def test_real_compose_preserves_single_and_split_graphs(compose_context, name, node, present, absent):
    deployment = manifest.get_deployment(ROOT, compose_context, name)
    selection = deployment.select(compose_context, "humble", False, node=node)
    result = compose.compose_capture(deployment, selection, ["config", "--format", "json"])
    services = json.loads(result.stdout)["services"]
    assert present <= services.keys() and not absent & services.keys()
    if node:
        bridge = services["zenoh-bridge"]
        assert "container_name" not in bridge
        assert bridge["environment"]["ROS_DOMAIN_ID"] == str(deployment.nodes[node]["rosDomainId"])
        mounts = {item["target"]: item["source"] for item in bridge["volumes"]}
        assert mounts["/config/zenoh.json5"] == str(deployment.directory / "config/zenoh.json5")
        assert mounts["/etc/cyclonedds/cyclonedds.xml"] == str(ROOT / "deployments/shared/cyclonedds.xml")
    if node in ("scenario", "carla"):
        assert set(services) == present
    if node == "scenario":
        assert "pid" not in services["scenario_simulator"]
    if name == "carla-simulation" and node == "autoware":
        assert "carla-interface" not in services["vehicle"].get("depends_on", {})


@pytest.mark.parametrize(("override", "rule"), [
    ("", None), ('  control:\n    command: ["true"]\n', "command"),
    ('  control:\n    volumes:\n      - ./config:/opt/autoware/config:ro\n', "internal-mount"),
])
def test_real_integrator_contract_checks_compiled_models(tmp_path, compose_context, override, rule):
    kit = tmp_path / "kit"
    shutil.copytree(ROOT / "examples/custom-kit", kit, ignore=shutil.ignore_patterns("build", "install", "log"))
    path = kit / "openadkit.json"
    document = json.loads(path.read_text())
    document["extends"] = str(ROOT)
    path.write_text(json.dumps(document))
    directory = kit / "deployments/custom-planning"
    (directory / "config.env").write_text("VEHICLE_ID=custom\n")
    with (directory / "docker-compose.yaml").open("a") as output:
        output.write(override)
    result = subprocess.run([str(ROOT / "openadkit"), "validate", "custom-planning", "--json"],
                            cwd=kit, env=dict(os.environ), text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["overlayConformant"] is (rule is None)
    assert {warning["rule"] for warning in report["overlayWarnings"]} == ({rule} if rule else set())
    assert all(warning.get("service") != "acme-probe" for warning in report["overlayWarnings"])
