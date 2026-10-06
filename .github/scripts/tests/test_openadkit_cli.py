"""Risk-focused CLI contracts; Docker is recorded, never started by this suite."""

import hashlib
import io
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "cli"))

import compose as cli_compose  # noqa: E402
import data as cli_data  # noqa: E402
import manifest as cli_manifest  # noqa: E402

ENTRYPOINT = ROOT / "openadkit"
COMPONENT_IMAGES = json.loads((ROOT / "openadkit.json").read_text())["componentImages"]
PIN = f"registry.example/image@sha256:{'a' * 64}"
OTHER_PIN = f"registry.example/custom@sha256:{'b' * 64}"
ARCH = {"x86_64": "amd64", "aarch64": "arm64"}.get(platform.machine(), platform.machine())
ISOLATED_ENV = (
    "XDG_CONFIG_HOME", "XDG_STATE_HOME", "OPENADKIT_CONFIG_DIR", "OPENADKIT_STATE_DIR",
    "OPENADKIT_KIT", "OPENADKIT_DELEGATED", "COMPOSE_FILE",
)


def executable(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(0o755)


def command(program, *args, home, bin_dir, cwd=None, **extra_env):
    home.mkdir(parents=True, exist_ok=True)
    env = {key: value for key, value in os.environ.items() if key not in ISOLATED_ENV}
    env.update(HOME=str(home), PATH=f"{bin_dir}:{os.environ['PATH']}")
    return subprocess.run(
        [str(program), *map(str, args)], cwd=cwd, env=env | extra_env,
        text=True, capture_output=True, timeout=30,
    )


def run_cli(root, *args, directory=None, **env):
    return command(root / "openadkit", *args, home=root.parent / "home",
                   bin_dir=root.parent / "bin", cwd=directory or root, **env)


def manifest(*, data=None, gpu=False, nodes=False):
    document = {
        "schemaVersion": 2, "name": "example", "description": "Test deployment",
        "compose": {"files": ["docker-compose.yaml"], "gpuFiles": ["gpu.yaml"] if gpu else [],
                    "profiles": [], "resetServices": [], "waitTimeout": 1},
        "requirements": {"architectures": ["amd64", "arm64"], "rosDistros": ["humble", "jazzy"],
                         "gpu": "optional" if gpu else "none"},
        "data": data or [],
    }
    if nodes:
        document["nodes"] = {
            name: {"rosDomainId": domain, "files": [f"compose.{name}.yaml"],
                   "resetServices": [], "requiredEnv": ["NODE_TOKEN"] if domain == 2 else []}
            for name, domain in (("primary", 1), ("secondary", 2))
        }
    return document


def runtime_tree(tmp_path, *, release=False, document=None, config="MAP_PATH=$HOME/data/map\n"):
    root = tmp_path / "runtime"
    root.mkdir(parents=True)
    shutil.copy2(ENTRYPOINT, root / "openadkit")
    shutil.copytree(ROOT / "cli", root / "cli", ignore=shutil.ignore_patterns("__pycache__"))
    directory = root / "deployments/example"
    directory.mkdir(parents=True)
    document = document or manifest()
    (directory / "deployment.json").write_text(json.dumps(document))
    (directory / "config.env").write_text(config)
    files = document["compose"]["files"] + document["compose"]["gpuFiles"]
    files += [file for node in document.get("nodes", {}).values() for file in node["files"]]
    for file in files:
        (directory / file).write_text("services:\n  app:\n    image: busybox:1.36.1\n")
    if document["compose"]["gpuFiles"]:
        (directory / "config.gpu.env").write_text("VALUE=base-gpu\nBASE_GPU=1\n")
    context = {
        "schemaVersion": 2, "kind": "release" if release else "repository",
        "defaultRosDistro": "humble", "componentImages": COMPONENT_IMAGES,
        "deployments": {"example": {"path": "deployments/example"}},
    }
    if release:
        context.update(version="v1.2.3", shared={},
                       autoware={"version": "1.8.0", "ref": "a" * 40, "lockSha256": "b" * 64},
                       images={distro: dict.fromkeys(COMPONENT_IMAGES.values(), PIN)
                               for distro in ("humble", "jazzy")})
        context["deployments"]["example"]["checksum"] = cli_manifest.deployment_checksum(directory)
    else:
        context["imagePrefixComponent"] = "registry.example/openadkit"
    (root / "openadkit.json").write_text(json.dumps(context))
    return root, directory


def edit_kit(root, change):
    path = root / "openadkit.json"
    document = json.loads(path.read_text())
    change(document)
    path.write_text(json.dumps(document))


def fake_docker(tmp_path, *, projects=(), daemon=0, config=0, runtimes='{"nvidia": {}}'):
    """One stateful stub shared by runtime and integrator subprocess tests."""
    calls = tmp_path / "docker-calls"
    live = tmp_path / "projects.json"
    live.write_text(json.dumps([{"Name": name, "Status": "running(1)"} for name in projects]))
    executable(tmp_path / "bin/docker", f'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
text = " ".join(args)
with open({str(calls)!r}, "a") as output:
    env = {{name: value for name, value in os.environ.items()
           if name.startswith("OPENADKIT_") or name in ("API_IMAGE", "VALUE", "ROS_DISTRO")}}
    output.write(json.dumps({{"args": args, "env": env}}) + "\\n")
live = Path({str(live)!r})
if text == "info":
    sys.exit({daemon})
if text == "info --format {{{{json .Runtimes}}}}":
    print({runtimes!r})
elif text == "compose ls --format json":
    print(live.read_text())
elif "config --format json" in text:
    print('{{"services": {{}}}}')
elif "config --services" in text:
    print("app\\nacme")
elif "config --quiet" in text:
    sys.exit({config})
elif "up --detach" in text:
    project = args[args.index("--project-name") + 1]
    rows = json.loads(live.read_text())
    if not any(row["Name"] == project for row in rows):
        rows.append({{"Name": project, "Status": "running(1)"}})
    live.write_text(json.dumps(rows))
''')
    return calls


def recorded(calls):
    return [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []


def site_config(root, text, name="example"):
    path = root.parent / f"home/.config/openadkit/{name}.env"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def integrator_kit(tmp_path, root, *, extends=None, artifacts=None):
    kit = tmp_path / "kit"
    directory = kit / "deployments/custom"
    directory.mkdir(parents=True)
    (kit / "openadkit.json").write_text(json.dumps({
        "schemaVersion": 2, "kind": "kit", "extends": extends or str(root),
        "deployments": {"custom": {"path": "deployments/custom"}}, "artifacts": artifacts or {},
    }))
    (directory / "deployment.json").write_text(json.dumps({
        "schemaVersion": 2, "name": "custom", "description": "Integrator deployment",
        "base": "example", "compose": {"files": ["docker-compose.yaml"]},
    }))
    (directory / "config.env").write_text("VALUE=kit\n")
    (directory / "docker-compose.yaml").write_text(
        "include:\n  - ${OPENADKIT_BASE_DEPLOYMENT}/docker-compose.yaml\n"
        "services:\n  acme:\n    image: busybox:1.36.1\n"
    )
    return kit


# Install/upgrade fixtures deliberately contain no runtime deployment inventory.
def release_bin(tmp_path, version="v1.2.3", *, bad_checksum=False, member=None):
    release = tmp_path / version
    release.mkdir()
    root_name = f"openadkit-{version}"
    bundle = release / f"{root_name}.tar.gz"
    files = {"openadkit": ENTRYPOINT.read_bytes(), "cli/main.py": b'print("ok")\n',
             "openadkit.json": json.dumps({"schemaVersion": 2, "kind": "release", "version": version}).encode()}
    files.update({f"cli/{name}.py": (ROOT / f"cli/{name}.py").read_bytes() for name in ("compose", "manifest")})
    if member:
        files[member] = "/etc/passwd" if member == "link" else b"escape"
    with tarfile.open(bundle, "w:gz", format=tarfile.USTAR_FORMAT) as archive:
        for name, payload in files.items():
            info = tarfile.TarInfo(f"{root_name}/{name}")
            info.mode = 0o755 if name == "openadkit" else 0o644
            if isinstance(payload, str):
                info.type, info.linkname = tarfile.SYMTYPE, payload
                archive.addfile(info)
            else:
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
    (release / "release-metadata.json").write_text(json.dumps({
        "openadkit_version": version, "bundles": [{"name": bundle.name,
        "sha256": "0" * 64 if bad_checksum else hashlib.sha256(bundle.read_bytes()).hexdigest()}],
    }))
    bin_dir = release / "bin"
    executable(bin_dir / "curl", f'''#!/usr/bin/env python3
import shutil, sys
from pathlib import Path
args = sys.argv[1:]
url = next(arg for arg in args if arg.startswith("http"))
shutil.copyfile(Path({str(release)!r}) / url.rsplit("/", 1)[-1], args[args.index("-o") + 1])
''')
    return bin_dir


def install(tmp_path, bin_dir, *args):
    return command(ENTRYPOINT, "install", "--destination", tmp_path / "home/kit", *args,
                   home=tmp_path / "home", bin_dir=bin_dir)


def installed(tmp_path, version="v1.2.3"):
    return tmp_path / f"home/kit/openadkit-{version}/openadkit"


def test_install_upgrade_and_uninstall_preserve_kept_versions(tmp_path):
    assert install(tmp_path, release_bin(tmp_path)).returncode == 0
    launcher = tmp_path / "home/.local/bin/openadkit"
    assert launcher.resolve() == installed(tmp_path)
    newer = release_bin(tmp_path, "v1.3.0")
    result = command(launcher, "upgrade", home=tmp_path / "home", bin_dir=newer)
    assert result.returncode == 0, result.stderr
    assert launcher.resolve() == installed(tmp_path, "v1.3.0")
    assert installed(tmp_path).is_file()
    fake_docker(tmp_path)
    result = command(launcher, "uninstall", home=tmp_path / "home", bin_dir=tmp_path / "bin")
    assert result.returncode == 0, result.stderr
    assert not launcher.exists() and not installed(tmp_path, "v1.3.0").exists()
    assert installed(tmp_path).is_file()


@pytest.mark.parametrize(("options", "message"), [
    ({"bad_checksum": True}, "checksum verification failed"),
    ({"member": "../escape"}, "unsafe bundle member"),
    ({"member": "link"}, "unsupported bundle member"),
])
def test_install_rejects_corrupt_or_unsafe_bundle(tmp_path, options, message):
    result = install(tmp_path, release_bin(tmp_path, **options))
    assert result.returncode != 0 and message in result.stderr
    assert not (tmp_path / "home/kit").exists()
    assert not (tmp_path / "escape").exists()


def test_failed_replacement_restores_previous_release(tmp_path):
    bin_dir = release_bin(tmp_path)
    assert install(tmp_path, bin_dir).returncode == 0
    root = installed(tmp_path).parent
    (root / "marker").write_text("previous")
    executable(bin_dir / "mv", "#!/usr/bin/env bash\n"
               f'if [[ $# -eq 2 && "$2" == "{root}" && "$1" == *".openadkit-stage."* ]]; then exit 1; fi\n'
               f'exec {shutil.which("mv")} "$@"\n')
    result = install(tmp_path, bin_dir, "--force")
    assert result.returncode != 0 and "could not replace" in result.stderr
    assert (root / "marker").read_text() == "previous"
    assert installed(tmp_path).is_file()
    assert (tmp_path / "home/.local/bin/openadkit").resolve() == installed(tmp_path)
    assert not list(root.parent.glob(".openadkit-*"))


def test_failed_upgrade_leaves_launcher_on_the_old_release(tmp_path):
    assert install(tmp_path, release_bin(tmp_path)).returncode == 0
    result = command(installed(tmp_path), "upgrade", home=tmp_path / "home",
                     bin_dir=release_bin(tmp_path, "v1.3.0", bad_checksum=True))
    assert result.returncode != 0 and "checksum verification failed" in result.stderr
    assert (tmp_path / "home/.local/bin/openadkit").resolve() == installed(tmp_path)
    assert not installed(tmp_path, "v1.3.0").exists()


def test_upgrade_never_downgrades(tmp_path):
    assert install(tmp_path, release_bin(tmp_path, "v1.3.0")).returncode == 0
    result = command(installed(tmp_path, "v1.3.0"), "upgrade", home=tmp_path / "home", bin_dir=release_bin(tmp_path))
    assert result.returncode == 0 and "nothing to upgrade" in result.stdout
    assert (tmp_path / "home/.local/bin/openadkit").resolve() == installed(tmp_path, "v1.3.0")


@pytest.mark.parametrize("unsafe", ["running", "launcher"])
def test_uninstall_refuses_unsafe_state(tmp_path, unsafe):
    assert install(tmp_path, release_bin(tmp_path)).returncode == 0
    launcher = tmp_path / "home/.local/bin/openadkit"
    fake_docker(tmp_path, projects=["openadkit-example"] if unsafe == "running" else [])
    if unsafe == "launcher":
        launcher.unlink()
        launcher.write_text("user launcher")
    result = command(installed(tmp_path), "uninstall", home=tmp_path / "home", bin_dir=tmp_path / "bin")
    assert result.returncode != 0
    assert ("stop running deployments" if unsafe == "running" else "non-symlink launcher") in result.stderr
    assert installed(tmp_path).is_file() and launcher.exists()


@pytest.mark.parametrize("release", [False, True])
def test_image_and_env_priority_reaches_compose(tmp_path, release):
    root, directory = runtime_tree(tmp_path, release=release, document=manifest(gpu=True),
                                   config="API_IMAGE=base\nVALUE=base\n")
    site_config(root, f"API_IMAGE={OTHER_PIN}\nVALUE=site\n")
    calls = fake_docker(tmp_path)
    result = run_cli(root, "validate", "example", "--gpu", API_IMAGE="shell", VALUE="shell")
    assert result.returncode == 0, result.stderr
    first = recorded(calls)[0]
    assert first["env"].get("VALUE") is None  # Compose, not the shell, loads file-defined values.
    assert first["env"].get("API_IMAGE") == (PIN if release else OTHER_PIN)
    env_files = [first["args"][index + 1] for index, arg in enumerate(first["args"]) if arg == "--env-file"]
    assert env_files == [str(directory / "config.env"), str(directory / "config.gpu.env"),
                         str(tmp_path / "home/.config/openadkit/example.env")]


@pytest.mark.parametrize("problem", ["mutable", "missing"])
def test_release_image_failures_prevent_compose(tmp_path, problem):
    root, _ = runtime_tree(tmp_path, release=True)
    edit_kit(root, lambda kit: kit["images"]["humble"].update(api="registry.example/api:latest")
             if problem == "mutable" else kit["images"]["humble"].pop("api"))
    calls = fake_docker(tmp_path)
    result = run_cli(root, "validate", "example")
    assert result.returncode != 0
    assert ("digest-pinned" if problem == "mutable" else "missing component image") in result.stderr
    assert recorded(calls) == []


@pytest.mark.parametrize("constraint", ["distro", "gpu-architecture"])
def test_unsupported_runtime_selection_fails_before_compose(tmp_path, constraint):
    document = manifest(gpu=True)
    document["requirements"].update(architectures=[ARCH, "other-arch"], rosDistros=["humble"], gpuArchitectures=["other-arch"])
    root, _ = runtime_tree(tmp_path, document=document)
    calls = fake_docker(tmp_path)
    args = ["--ros-distro", "jazzy"] if constraint == "distro" else ["--gpu"]
    result = run_cli(root, "validate", "example", *args)
    assert result.returncode != 0
    assert ("does not support ROS distro jazzy" if constraint == "distro" else f"GPU mode does not support {ARCH}") in result.stderr
    assert recorded(calls) == []


@pytest.mark.parametrize(("options", "args", "message"), [
    ({"daemon": 1}, [], "Docker daemon"),
    ({"runtimes": "{}"}, ["--gpu"], "NVIDIA Container Toolkit"),
    ({"config": 1}, [], "failed"),
])
def test_run_preflight_does_not_touch_data_or_start_containers(tmp_path, options, args, message):
    root, _ = runtime_tree(tmp_path, document=manifest(gpu=True))
    calls = fake_docker(tmp_path, **options)
    result = run_cli(root, "run", "example", *args)
    assert result.returncode != 0 and message in result.stderr
    assert not any("up" in row["args"] or "pull" in row["args"] for row in recorded(calls))
    assert not (tmp_path / "home/data").exists()


def test_split_node_run_discovery_and_safe_stop(tmp_path):
    root, _ = runtime_tree(tmp_path, document=manifest(nodes=True))
    calls = fake_docker(tmp_path)
    blocked = run_cli(root, "run", "example", "--node", "secondary", "--pull", "never")
    assert blocked.returncode != 0 and "NODE_TOKEN" in blocked.stderr
    assert recorded(calls) == []
    result = run_cli(root, "run", "example", "--node", "secondary", "--pull", "never", NODE_TOKEN="token")
    assert result.returncode == 0, result.stderr
    rows = recorded(calls)
    up = next(row for row in rows if "up" in row["args"])
    assert "openadkit-example-secondary" in up["args"]
    assert up["env"]["OPENADKIT_ROS_DOMAIN_ID"] == "2"
    assert str(root / "deployments/example/compose.secondary.yaml") in up["args"]
    assert not any("zenoh" in arg or arg.endswith("docker-compose.yaml") for arg in up["args"])
    calls.write_text("")
    result = run_cli(root, "stop", "example")
    assert result.returncode == 0, result.stderr
    down = next(row["args"] for row in recorded(calls) if "down" in row["args"])
    assert "openadkit-example-secondary" in down and "--volumes" not in down


@pytest.mark.parametrize(("projects", "args", "message"), [
    (["openadkit-example-primary"], [], "already running as node primary"),
    (["openadkit-example"], ["--node", "primary"], "already running as single-host"),
    (["openadkit-other"], [], "already running"),
])
def test_incompatible_live_projects_cannot_be_started_over(tmp_path, projects, args, message):
    root, _ = runtime_tree(tmp_path, document=manifest(nodes=True))
    edit_kit(root, lambda kit: kit["deployments"].update(other={"path": "deployments/other"}))
    calls = fake_docker(tmp_path, projects=projects)
    result = run_cli(root, "run", "example", "--pull", "never", *args)
    assert result.returncode != 0 and message in result.stderr
    assert not any("up" in row["args"] for row in recorded(calls))


def test_several_live_nodes_require_an_explicit_stop_target(tmp_path):
    root, _ = runtime_tree(tmp_path, document=manifest(nodes=True))
    calls = fake_docker(tmp_path, projects=["openadkit-example-primary", "openadkit-example-secondary"])
    result = run_cli(root, "stop", "example")
    assert result.returncode != 0 and "choose one with --node" in result.stderr
    assert not any("down" in row["args"] for row in recorded(calls))


@pytest.mark.parametrize("unsafe", ["missing", "symlink", "escape"])
def test_required_node_files_are_checked_before_compose(tmp_path, unsafe):
    document = manifest(nodes=True)
    document["nodes"]["primary"]["requiredFiles"] = ["../outside" if unsafe == "escape" else "allowlist.json"]
    root, directory = runtime_tree(tmp_path, document=document)
    if unsafe == "symlink":
        outside = tmp_path / "outside"
        outside.write_text("{}")
        (directory / "allowlist.json").symlink_to(outside)
    calls = fake_docker(tmp_path)
    result = run_cli(root, "validate", "example", "--node", "primary")
    assert result.returncode != 0
    assert {"missing": "missing required node file", "symlink": "symlinked required node file",
            "escape": "safe relative path"}[unsafe] in result.stderr
    assert recorded(calls) == []


def files_resource(tmp_path, *, env="MAP_PATH", name="dataset", **extra):
    source = tmp_path / f"{name}.txt"
    source.write_text("replacement")
    return {"name": name, "kind": "files", "destinationEnv": env, "requiredFiles": ["required.txt"],
            "files": [{"path": "required.txt", "url": source.as_uri(),
                       "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}], **extra}


def test_only_explicit_fetch_force_replaces_managed_data(tmp_path):
    root, _ = runtime_tree(tmp_path, document=manifest(data=[files_resource(tmp_path)]))
    target = tmp_path / "home/data/map"
    target.mkdir(parents=True)
    calls = fake_docker(tmp_path)
    result = run_cli(root, "run", "example", "--pull", "never")
    assert result.returncode != 0 and "openadkit fetch example --force" in result.stderr
    assert not any("up" in row["args"] for row in recorded(calls))
    assert run_cli(root, "run", "example", "--force").returncode == 2
    assert "refusing to replace" in run_cli(root, "fetch", "example", "--force").stderr
    (target / cli_data.MARKER).write_text("{}")
    result = run_cli(root, "fetch", "example", "--force")
    assert result.returncode == 0, result.stderr
    assert (target / "required.txt").read_text() == "replacement"
    assert json.loads((target / cli_data.MARKER).read_text()) == {"resource": "dataset"}
    (target / "required.txt").write_text("keep existing")
    assert run_cli(root, "fetch", "example").returncode == 0
    assert (target / "required.txt").read_text() == "keep existing"
    assert run_cli(root, "run", "example", "--pull", "never").returncode == 0


def test_checksum_failure_preserves_managed_data_and_cleans_staging(tmp_path, monkeypatch):
    # Exercise download validation, not the earlier unmanaged-target refusal.
    resource = files_resource(tmp_path)
    resource["files"][0]["sha256"] = "0" * 64
    resource["generatedFiles"] = {}
    target = tmp_path / "installed"
    target.mkdir()
    (target / cli_data.MARKER).write_text("{}")
    (target / "required.txt").write_text("original")
    monkeypatch.setattr(cli_data.time, "sleep", lambda _: None)
    selection = cli_manifest.Selection("humble", False, None, {}, {"MAP_PATH": str(target)})
    with pytest.raises(cli_manifest.OpenADKitError, match="checksum mismatch"):
        cli_data.install_resource(resource, selection, True)
    assert (target / "required.txt").read_text() == "original"
    assert not list(tmp_path.glob(".dataset.stage.*"))


@pytest.mark.parametrize("unsafe", ["traversal", "absolute", "symlink", "duplicate"])
def test_zip_validation_rejects_unsafe_members(tmp_path, unsafe):
    archive = tmp_path / "unsafe.zip"
    info = zipfile.ZipInfo({"traversal": "dataset/../escape", "absolute": "/escape"}.get(unsafe, "dataset/file"))
    if unsafe == "symlink":
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr(info, "payload")
        if unsafe == "duplicate":
            with pytest.warns(UserWarning, match="Duplicate name"):
                output.writestr(info, "again")
    stage = tmp_path / "stage"
    with pytest.raises(cli_manifest.OpenADKitError, match="ZIP member"):
        cli_data.extract_zip(archive, stage, "dataset")
    assert not stage.exists() and not (tmp_path / "escape").exists()


def test_zip_fetch_publishes_validated_data(tmp_path):
    archive = tmp_path / "data.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("dataset/required.txt", "map")
    resource = {"name": "dataset", "kind": "zip", "destinationEnv": "MAP_PATH", "expectedRoot": "dataset",
                "url": archive.as_uri(), "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "requiredFiles": ["required.txt"]}
    root, _ = runtime_tree(tmp_path, document=manifest(data=[resource]))
    result = run_cli(root, "fetch", "example")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "home/data/map/required.txt").read_text() == "map"
    fake_docker(tmp_path)
    result = run_cli(root, "clean", "example", "--data")
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "home/data/map").exists()


@pytest.mark.parametrize("unsafe", ["unmanaged", "file", "symlink", "marker-symlink", "running"])
def test_clean_checks_all_targets_before_deleting_anything(tmp_path, unsafe):
    resources = [files_resource(tmp_path), files_resource(tmp_path, env="SECOND_PATH", name="second")]
    root, _ = runtime_tree(tmp_path, document=manifest(data=resources),
                           config="MAP_PATH=$HOME/data/map\nSECOND_PATH=$HOME/data/second\n")
    first, second = tmp_path / "home/data/map", tmp_path / "home/data/second"
    for target in (first, second):
        target.mkdir(parents=True)
        (target / cli_data.MARKER).write_text("{}")
        (target / "required.txt").write_text("keep")
    if unsafe == "unmanaged":
        (second / cli_data.MARKER).unlink()
    elif unsafe == "file":
        shutil.rmtree(second)
        second.write_text("keep")
    elif unsafe == "symlink":
        second.rename(tmp_path / "outside")
        second.symlink_to(tmp_path / "outside")
    elif unsafe == "marker-symlink":
        (second / cli_data.MARKER).unlink()
        (second / cli_data.MARKER).symlink_to(first / cli_data.MARKER)
    fake_docker(tmp_path, projects=["openadkit-example"] if unsafe == "running" else [])
    result = run_cli(root, "clean", "example", "--data")
    assert result.returncode != 0
    message = "example is running" if unsafe == "running" else (
        "refusing to remove symlinked data" if unsafe == "symlink" else "not installed by openadkit"
    )
    assert message in result.stderr
    assert (first / "required.txt").read_text() == "keep"
    assert second.exists()


def test_fetch_checks_every_destination_before_download(tmp_path):
    resources = [files_resource(tmp_path), files_resource(tmp_path, env="SECOND_PATH", name="second")]
    root, _ = runtime_tree(tmp_path, document=manifest(data=resources),
                           config="MAP_PATH=$HOME/data/map\nSECOND_PATH=relative\n")
    result = run_cli(root, "fetch", "example")
    assert result.returncode != 0 and "must be absolute" in result.stderr
    assert not (tmp_path / "home/data").exists()


@pytest.mark.parametrize("base_refs", [{"ref": PIN}, {"distros": {"humble": PIN, "jazzy": PIN}}])
def test_kit_artifact_fallback_and_wildcard_override(tmp_path, base_refs):
    root, _ = runtime_tree(tmp_path)
    edit_kit(root, lambda doc: doc.update(artifacts={"EXTERNAL_IMAGE": {"workload": "api", **base_refs}}))
    kit = integrator_kit(tmp_path, root, artifacts={"EXTERNAL_IMAGE": {"workload": "api", "distros": {"humble": OTHER_PIN}}})
    context = cli_manifest.load_kit(kit)
    assert context.artifact_environment("humble")["EXTERNAL_IMAGE"] == OTHER_PIN
    assert context.artifact_environment("jazzy")["EXTERNAL_IMAGE"] == PIN
    edit_kit(kit, lambda doc: doc.update(artifacts={"EXTERNAL_IMAGE": {"workload": "api", "ref": OTHER_PIN}}))
    assert cli_manifest.load_kit(kit).artifact_environment("jazzy")["EXTERNAL_IMAGE"] == OTHER_PIN


@pytest.mark.parametrize("release", [False, True])
def test_kit_inherits_pins_gpu_env_and_layers(tmp_path, monkeypatch, release):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    for name in ISOLATED_ENV:
        monkeypatch.delenv(name, raising=False)
    root, base = runtime_tree(tmp_path, release=release,
                              document=manifest(gpu=True, data=[files_resource(tmp_path)]), config="VALUE=base\nMAP_PATH=$HOME/data/map\n")
    edit_kit(root, lambda doc: doc.update(artifacts={"INHERITED_IMAGE": {"workload": "sim", "ref": PIN}}))
    kit = integrator_kit(tmp_path, root, artifacts={"API_IMAGE": {"workload": "api", "ref": OTHER_PIN}})
    directory = kit / "deployments/custom"
    (directory / "config.gpu.env").write_text("VALUE=kit-gpu\n")
    for path in (base / "config", directory / "config", directory / "overlay_ws"):
        path.mkdir()
    site_config(root, "VALUE=site\n", name="custom")
    context = cli_manifest.load_kit(kit)
    deployment = cli_manifest.get_deployment(kit, context, "custom")
    assert deployment.requirements["gpu"] == "optional" and deployment.data[0]["name"] == "dataset"
    selection = deployment.select(context, "humble", True)
    assert deployment.compose_files(True) == [directory / "docker-compose.yaml", base / "gpu.yaml"]
    assert selection.environment["VALUE"] == "site" and selection.environment["BASE_GPU"] == "1"
    assert selection.injections["API_IMAGE"] == OTHER_PIN
    assert selection.injections["OPENADKIT_BASE_DEPLOYMENT"] == str(base)
    calls = fake_docker(tmp_path)
    result = run_cli(root, "validate", "custom", "--gpu", directory=kit)
    assert result.returncode == 0, result.stderr
    env = recorded(calls)[0]["env"]
    assert [env[name] for name in ("OPENADKIT_CONFIG_BASE", "OPENADKIT_CONFIG_DEPLOYMENT", "OPENADKIT_OVERLAY_WS")] == [
        str(base / "config"), str(directory / "config"), str(directory / "overlay_ws"),
    ]
    bom = json.loads(run_cli(root, "version", "--json", directory=kit).stdout)["bom"]
    assert bom["artifacts"]["INHERITED_IMAGE"]["ref"] == PIN
    assert (bom["images"] is not None) is release


@pytest.mark.parametrize("available", [False, True])
def test_pinned_kit_uses_its_release_cli_or_fails_with_install_guidance(tmp_path, available):
    root, _ = runtime_tree(tmp_path)
    kit = integrator_kit(tmp_path, root, extends="v1.2.3")
    record = tmp_path / "delegated"
    if available:
        pinned = tmp_path / "home/.local/share/openadkit/openadkit-v1.2.3"
        pinned.mkdir(parents=True)
        (pinned / "openadkit.json").write_text('{"schemaVersion":2,"kind":"release"}')
        executable(pinned / "openadkit", "#!/usr/bin/env bash\n"
                   f'printf "%s|%s|%s\\n" "$OPENADKIT_KIT" "$OPENADKIT_DELEGATED" "$*" > "{record}"\n')
    result = run_cli(root, "run", "custom", "--pull", "never", directory=kit)
    assert (result.returncode == 0) is available, result.stderr
    if available:
        assert record.read_text().strip() == f"{kit}|1|run custom --pull never"
    else:
        assert "openadkit install --version v1.2.3" in result.stderr


def test_overlay_contract_distinguishes_base_changes_from_added_services():
    mount = {"type": "bind", "source": "/base/dds.xml", "target": "/etc/dds.xml", "read_only": True}
    base = {"app": {"command": ["launch"], "image": PIN, "volumes": [mount]}}
    assert cli_compose.overlay_warnings(base, base, set()) == []
    changed = {"app": {"command": ["other"], "image": OTHER_PIN, "volumes": [
        mount, {"type": "bind", "source": "/kit", "target": "/opt/autoware/config"},
    ]}, "extra": {"command": ["custom"], "image": "custom"}}
    warnings = cli_compose.overlay_warnings(base, changed, {"TYPO"})
    assert [warning["rule"] for warning in warnings] == ["command", "image", "internal-mount", "variable"]
    assert all(warning.get("service") != "extra" for warning in warnings)
