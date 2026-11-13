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
import catalog  # noqa: E402
import compose  # noqa: E402
import settings  # noqa: E402

INVENTORY = json.loads((ROOT / ".github/image-inventory.json").read_text())


def test_inventory_bake_and_runtime_catalog_agree():
    bake = (ROOT / "components/docker-bake.hcl").read_text()
    targets = {image["target"] for image in INVENTORY["images"]}
    # universe-common-build is CI's unpublished compile base for components.
    assert set(re.findall(r'^target\s+"(?!_|docker-metadata-action-)([\w-]+)"', bake, re.M)) == targets | {"universe-common-build"}
    assert set(re.findall(r'target\s+"docker-metadata-action-([\w-]+)"', bake)) == targets
    # Bake resolves a name to a group first: a group named like a target hides it.
    assert not set(re.findall(r'^group\s+"([\w-]+)"', bake, re.M)) & targets
    kit = json.loads((ROOT / "openadkit.json").read_text())
    assert set(kit["componentImages"].values()) == {image["target"] for image in INVENTORY["images"] if image["stage"] == "component"}
    resolved = matrices.build_matrices(INVENTORY)
    index = {(row["target"], row["ros-distro"]): row["arches"] for row in resolved["manifest_matrix"]["include"]}
    assert index[("planning", "humble")] == "amd64 arm64"
    assert index[("control", "humble")] == "amd64 arm64"
    assert index[("sensing-perception-cuda", "jazzy")] == "amd64"
    assert index[("planning-cuda", "jazzy")] == "amd64"
    assert "simulator" in {row["target"] for row in resolved["component_matrix"]["include"]}
    assert set(resolved) == {"common_matrix", "component_matrix", "manifest_matrix"}


@pytest.mark.parametrize(("path", "expected", "flags"), [
    ("components/universe-common/Dockerfile", {image["target"] for image in INVENTORY["images"]}, {"use_local_common": True}),
    (".dockerignore", {image["target"] for image in INVENTORY["images"]}, {"use_local_common": True}),
    (".github/autoware.ref", {image["target"] for image in INVENTORY["images"]}, {"use_local_common": True}),
    ("components/sensing-perception/Dockerfile.cuda", {"sensing-perception-cuda"}, {}),
    ("components/planning/Dockerfile.cuda", {"planning-cuda"}, {}),
    ("components/planning/Dockerfile", {"planning"}, {}),
    ("components/sensing-perception/scripts/build.sh", {"sensing-perception", "sensing-perception-cuda"}, {}),
    ("components/simulator/Dockerfile", {"simulator"}, {}),
    ("docs/index.md", set(), {}),
    (".github/autoware-patches/universe/autoware_universe/0001-fix.patch",
     {image["target"] for image in INVENTORY["images"]}, {"use_local_common": True}),
    (".github/scripts/autoware_patches.py", {image["target"] for image in INVENTORY["images"]}, {"use_local_common": True}),
    ("components/visualizer/README.md", set(), {}),
    # Shared by every image.
    ("components/shared/runtime-deps.sh", {image["target"] for image in INVENTORY["images"]}, {}),
    # The pipeline alone: one small image proves it.
    (".github/scripts/build.py", {"api"}, {"use_local_common": False}),
    (".github/workflows/build-single-image-distro.yaml", {"api"}, {}),
    (".github/actions/build-image/action.yaml", {"api"}, {}),
    # Copied into the image, unlike the component's own README.
    ("components/visualizer/novnc/README.md", {"visualizer"}, {}),
])
def test_changed_inputs_select_required_builds(path, expected, flags):
    plan = matrices.build_single_image_plan(INVENTORY, [path])
    assert set(plan["targets_json"]) == expected
    assert all(plan[name] is value for name, value in flags.items())


def test_a_removed_component_builds_nothing(tmp_path, monkeypatch):
    # A deleted component's files are in the diff of the change that removes it.
    monkeypatch.setattr(matrices, "REPOSITORY", tmp_path)
    plan = matrices.build_single_image_plan(INVENTORY, ["components/carla-interface/Dockerfile"])
    assert plan["targets_json"] == []


def test_invalid_build_inputs_fail_closed(tmp_path, monkeypatch):
    # A component in the checkout but not in the inventory must be mapped.
    monkeypatch.setattr(matrices, "REPOSITORY", tmp_path)
    (tmp_path / "components/new-component").mkdir(parents=True)
    for options, message in [
        ({"target_input": "missing"}, "Unknown Bake target"),
        ({"distro": "rolling"}, "Unsupported ROS distro"),
        ({"changed_files": ["components/new-component/Dockerfile"]}, "Unmapped component build input"),
    ]:
        with pytest.raises(ValueError, match=message):
            matrices.build_single_image_plan(INVENTORY, **options)


@pytest.mark.parametrize(("target", "publish", "local"), [
    ("universe-common", True, False), ("sensing-perception-cuda", True, False), ("planning-cuda", True, False),
    ("simulator", True, False), ("api", False, False), ("simulator", False, True),
])
def test_shared_build_recipe_keeps_pins_provenance_and_local_graphs(target, publish, local):
    uri = "docker-image://example/base@sha256:" + "c" * 64
    prepared = {"build_tag": "123-1", "cache_scope": "main", "autoware_input_ref": "1.8.0", "autoware_ref_type": "tag",
                "autoware_ref": "a" * 40, "autoware_base_version": "1.8.0", "autoware_lock_sha256": "e" * 64,
                "upstream_images": json.dumps({"humble": {name: {"uri": uri} for name in ("core-devel", "base", "base-cuda-runtime", "base-cuda-devel")}}),
                "use_local_common": str(local).lower()}
    if not local:
        prepared.update(devel_context=uri, runtime_context=uri)
    recipe, targets = matrices.bake_recipe(INVENTORY, prepared, target, "humble", "linux/amd64", publish=publish,
                                           common_check=False, owner="example")
    row = recipe["target"][target]
    assert targets == (["universe-common-build", "universe-common-devel", "universe-common"]
                       if publish and target == "universe-common" else [target])
    common_build = "ghcr.io/example/openadkit-buildcache:universe-common-build-amd64-humble-123-1"
    if publish:
        # The project's own namespace, with plain keys so `docker inspect` reads
        # a label by its documented name; the OCI keys are metadata-action's.
        assert row["labels"] == {"org.autoware.openadkit.autoware-version": "1.8.0",
                                 "org.autoware.openadkit.autoware-ref": "a" * 40,
                                 "org.autoware.openadkit.autoware-lock-sha256": "e" * 64}
        assert not any('"' in key for key in row["labels"])
        assert row["cache-to"][0].endswith(",mode=max")
        assert (row["contexts"].get("autoware-base-cuda-devel") == uri) is target.endswith("-cuda")
        if target == "universe-common":
            # Per-build labels or provenance would change the compile base's
            # digest on every build and invalidate every component compile.
            build = recipe["target"]["universe-common-build"]
            assert build["tags"] == [common_build] and not build["labels"]
            assert build["attest"] == ["type=provenance,disabled=true"]
            # Nor may the build time: the config records it.
            assert build["args"]["SOURCE_DATE_EPOCH"] == matrices.COMPILE_BASE_EPOCH
            assert "SOURCE_DATE_EPOCH" not in row["args"]
            # The build and runtime stages keep separate caches; neither
            # export may overwrite the other.
            cache = "type=registry,ref=ghcr.io/example/openadkit-buildcache:{}-amd64-humble-main"
            assert build["cache-to"] == [cache.format("universe-common-build") + ",mode=max"]
            assert row["cache-to"] == [cache.format("universe-common") + ",mode=max"]
            assert "cache-to" not in recipe["target"]["universe-common-devel"]
            assert row["cache-from"] == [cache.format(name) for name in ("universe-common-build", "universe-common")]
        else:
            assert row["contexts"]["universe-common-devel"] == "docker-image://" + common_build
    else:
        assert not row["labels"] and "cache-to" not in row
        assert ("universe-common" in row["contexts"]) is (not local)
        assert "simulator" not in row["contexts"]


@pytest.mark.parametrize(("target", "common_check"), [("universe-common", True), ("api", False)])
def test_pull_requests_rebuild_common_from_the_registry_cache_only(target, common_check):
    # A multi-GB hand-over through the Actions cache stalled; each job builds
    # the common images again from main's registry cache instead.
    prepared = {"build_tag": "123-1", "cache_scope": "main", "use_local_common": "true"}
    recipe, _ = matrices.bake_recipe(INVENTORY, prepared, target, "humble", "linux/amd64", publish=False,
                                     common_check=common_check, owner="example")
    assert "type=gha" not in json.dumps(recipe) and "cache-to" not in json.dumps(recipe)
    cache = "type=registry,ref=ghcr.io/example/openadkit-buildcache:universe-common-amd64-humble-main"
    assert cache in recipe["target"][target]["cache-from"]


@pytest.mark.parametrize("path", ["components/universe-common/Dockerfile", "components/sensing-perception/Dockerfile.cuda"])
def test_stages_pin_ros_snapshot_and_runtime_checks_linked_libraries(path):
    text = (ROOT / path).read_text()
    devel, runtime = text.rsplit("\nFROM ", 1)
    pin = 'bash /tmp/ros-snapshot/ros-snapshot.sh "${ROS_SNAPSHOT}" --check'
    assert devel.index(pin) < devel.index("colcon build")
    assert runtime.index(pin) < runtime.index("bash /tmp/security-refresh.sh") < runtime.index("bash /tmp/check-linked-libs.sh") < runtime.index("COPY components/shared/entrypoint/")
    assert 'ENTRYPOINT ["/docker-entrypoint.sh", "/opt/openadkit/openadkit-hook.sh"]' in runtime


@pytest.fixture
def compose_context(tmp_path, monkeypatch):
    if shutil.which("docker") is None:
        pytest.skip("docker compose is required")
    # Keep Docker's own config: CI installs Compose v5 into ~/.docker/cli-plugins,
    # and without it Docker falls back to the runner's older plugin.
    monkeypatch.setenv("DOCKER_CONFIG", os.environ.get("DOCKER_CONFIG") or str(Path.home() / ".docker"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENADKIT_SETTINGS_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("OPENADKIT_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("ZENOH_LISTEN", "tcp/127.0.0.1:7447")
    monkeypatch.setenv("ZENOH_PEER", "tcp/127.0.0.1:7447")
    monkeypatch.setenv("REMOTE_PASSWORD", "ci-validate")
    monkeypatch.delenv("OPENADKIT_KIT", raising=False)
    monkeypatch.delenv("OPENADKIT_DELEGATED", raising=False)
    return catalog.load_catalog(ROOT)


@pytest.mark.parametrize(("name", "role", "present", "absent"), [
    ("scenario-simulation", None, {"scenario-simulator", "map", "mrm-state-relay", "visualizer"}, {"zenoh-bridge"}),
    ("scenario-simulation", "autoware", {"map", "zenoh-bridge", "mrm-state-relay"}, {"scenario-simulator", "visualizer"}),
    ("scenario-simulation", "scenario", {"scenario-simulator", "zenoh-bridge", "visualizer"},
     {"map", "vehicle", "mrm-state-relay"}),
    ("carla-simulation", None, {"carla", "carla-interface", "map", "visualizer"}, {"zenoh-bridge"}),
    ("carla-simulation", "autoware", {"map", "zenoh-bridge"}, {"carla", "carla-interface", "visualizer"}),
    ("carla-simulation", "carla", {"carla", "carla-interface", "carla-map-loader", "zenoh-bridge", "visualizer"},
     {"map", "vehicle"}),
])
def test_real_compose_preserves_single_and_split_graphs(compose_context, name, role, present, absent):
    deployment = catalog.get_deployment(ROOT, compose_context, name)
    selection = settings.resolve(deployment, compose_context, "humble", False, role=role)
    result = compose.run_compose(deployment, selection, ["config", "--format", "json"])
    services = json.loads(result.stdout)["services"]
    assert present <= services.keys() and not absent & services.keys()
    if role:
        bridge = services["zenoh-bridge"]
        assert "container_name" not in bridge
        assert bridge["environment"]["ROS_DOMAIN_ID"] == str(deployment.roles[role]["rosDomainId"])
        mounts = {item["target"]: item["source"] for item in bridge["volumes"]}
        assert mounts["/config/zenoh.json5"] == str(deployment.directory / "config/zenoh.json5")
        assert mounts["/etc/cyclonedds/cyclonedds.xml"] == str(ROOT / "deployments/shared/cyclonedds.xml")
    if role in ("scenario", "carla"):
        assert set(services) == present
    if role == "scenario":
        assert "pid" not in services["scenario-simulator"]
    if name == "carla-simulation" and role == "autoware":
        assert "carla-interface" not in services["vehicle"].get("depends_on", {})
    # The visualizer joins no PID namespace, and only the single-host graph waits on Autoware.
    if "visualizer" in services:
        assert "pid" not in services["visualizer"]
        assert ("map" in services["visualizer"].get("depends_on", {})) is (role is None)


def test_safety_island_simulation_keeps_planning_simulations_stack():
    """Safety Island Simulation repeats Planning Simulation's services, settings
    and map in its own files, so the copies must not drift apart."""
    planning, island = ROOT / "deployments/planning-simulation", ROOT / "deployments/safety-island-simulation"
    stack = (planning / "compose.yaml").read_text(encoding="utf-8")
    assert stack[stack.index("include:"):].rstrip() in (island / "compose.yaml").read_text(encoding="utf-8")

    def values(path):
        lines = path.read_text(encoding="utf-8").splitlines()
        return dict(line.split("=", 1) for line in lines if line and not line.startswith("#"))

    own = {"SAFETY_ISLAND_PATH", "SYSTEM_DIAGNOSTICS_GRAPH"}
    # The Diffusion Planner model belongs to the GPU mode, which this deployment does not have.
    expected = {name: value for name, value in values(planning / "settings.env").items() if name != "DIFFUSION_PLANNER_DATA_PATH"}
    assert {name: value for name, value in values(island / "settings.env").items() if name not in own} == expected

    base, standalone = (json.loads((path / "deployment.json").read_text(encoding="utf-8")) for path in (planning, island))
    assert standalone["verify"] == base["verify"]
    assert standalone["waitTimeout"] == base["waitTimeout"]
    assert [item for item in base["data"] if not item.get("gpu")] == standalone["data"][:1]


def test_real_kit_validates_against_its_source_base(tmp_path, compose_context):
    import validation_matrix
    [kit] = validation_matrix.make_example_kits(ROOT, tmp_path)
    assert json.loads((kit / "openadkit.json").read_text())["extends"] == str(ROOT)
    directory = kit
    # Documented host settings, used by the shared services and runtime.env.
    (directory / "settings.env").write_text(
        "VEHICLE_ID=custom\nCYCLONEDDS_NETWORK_INTERFACE=eth0\nWEBSOCKIFY_BIND=0.0.0.0\nRVIZ_GPU=off\n"
    )
    result = subprocess.run([str(ROOT / "openadkit"), "validate", "example-kit", "--json"],
                            cwd=kit, env=dict(os.environ), text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["base"] == "planning-simulation"


def test_kit_on_one_service_layer_owns_its_services_and_settings(tmp_path, compose_context):
    # A kit: carla-simulation's Autoware side, with its own CARLA.
    kit = tmp_path / "kit"
    directory = kit / "deployments/world"
    directory.mkdir(parents=True)
    (kit / "openadkit.json").write_text(json.dumps({
        "schemaVersion": 2, "kind": "kit", "extends": str(ROOT),
        "deployments": {"world": {"path": "deployments/world"}}, "externalImages": {},
    }))
    (directory / "deployment.json").write_text(json.dumps({
        "description": "Own simulator", "base": "carla-simulation",
    }))
    (directory / "settings.env").write_text("TOWN=Town01\n")
    (directory / "compose.yaml").write_text(
        "include:\n  - ${OPENADKIT_BASE_DEPLOYMENT}/compose.autoware.yaml\n"
        "services:\n"
        "  carla:\n    image: busybox:1.36.1\n    command: [\"sleep\", \"${TOWN}\"]\n"
    )
    result = subprocess.run([str(ROOT / "openadkit"), "validate", "world", "--gpu", "--json"],
                            cwd=kit, env=dict(os.environ), text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr


def test_kit_files_shared_by_deployments_and_host_reads_are_the_kits(tmp_path, compose_context):
    # A kit: a world file two deployments include, one of which
    # takes nothing from the base and reads the desktop's DISPLAY.
    kit = tmp_path / "kit"
    (kit / "deployments/shared").mkdir(parents=True)
    (kit / "openadkit.json").write_text(json.dumps({
        "schemaVersion": 2, "kind": "kit", "extends": str(ROOT),
        "deployments": {"manual": {"path": "deployments/manual"}}, "externalImages": {},
    }))
    world = '  carla:\n    image: busybox:1.36.1\n    command: ["sleep", "${TOWN}"]\n'
    (kit / "deployments/shared/world.yaml").write_text("services:\n" + world)
    directory = kit / "deployments/manual"
    directory.mkdir()
    (directory / "deployment.json").write_text(json.dumps({
        "description": "Drive by hand", "base": "carla-simulation",
    }))
    (directory / "settings.env").write_text("TOWN=Town01\n")
    (directory / "compose.yaml").write_text(
        "include:\n  - ../shared/world.yaml\n"
        "services:\n  manual:\n    image: busybox:1.36.1\n"
        "    environment:\n      DISPLAY: ${DISPLAY:?run from a desktop session}\n"
    )
    environment = dict(os.environ, DISPLAY=":1")
    result = subprocess.run([str(ROOT / "openadkit"), "validate", "manual", "--gpu", "--json"],
                            cwd=kit, env=environment, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr


def test_centerpoint_models_mount_where_the_cli_installs_them(compose_context, tmp_path):
    import data
    (tmp_path / "config").mkdir()
    (tmp_path / "config/logging-simulation.env").write_text("DATA_PATH=/srv/autoware_data\n")
    deployment = catalog.get_deployment(ROOT, compose_context, "logging-simulation")
    selection = settings.resolve(deployment, compose_context, "humble", True)
    resource = next(item for item in deployment.data if item["destinationEnv"] == "CENTERPOINT_DATA_PATH")
    result = compose.run_compose(deployment, selection, ["config", "--format", "json"])
    mounts = {item["target"]: item["source"] for item in json.loads(result.stdout)["services"]["perception"]["volumes"]}
    assert mounts["/autoware_data"] == "/srv/autoware_data"
    assert mounts["/autoware_data/lidar_centerpoint"] == str(data.resolve_destination(resource, selection))
