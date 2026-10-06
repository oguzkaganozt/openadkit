"""Release shell boundaries: immutable plans, safe publication and packaging."""

import hashlib
import json
import os
import subprocess
import tarfile

import pytest
from release_fixtures import (
    BUILD_TAG,
    DIGEST,
    RELEASE_SHA,
    ROOT,
    VERSION,
    WRITE_NOTES,
    build_images,
    executable,
    packager_env,
    run_packager,
    run_validator,
    write_plan,
)

MARKER = "<!-- openadkit-release-workflow:v1 -->\n"


@pytest.mark.parametrize(("version", "ref_type", "input_ref", "accepted"), [
    ("v2.0.0", "tag", "1.8.0", True),
    ("v2.0.0-rc.1", "sha", "a" * 40, True),
    ("v2.0.0", "sha", "a" * 40, False),
    ("v2.0.0-rc.1", "branch", "main", False),
    ("v2.0.0-rc.1", "sha", "abc123", False),
])
def test_release_ref_policy(tmp_path, version, ref_type, input_ref, accepted):
    build = tmp_path / "release-input/build"
    build.mkdir(parents=True)
    (build / "build-metadata.json").write_text(json.dumps({
        "openadkit_sha": RELEASE_SHA, "autoware_input_ref": input_ref,
        "autoware_ref_type": ref_type, "autoware_base_version": "1.8.0",
    }))
    result = run_validator(tmp_path, "validate_release_rules", VERSION=version)
    assert (result.returncode == 0) is accepted, result.stderr


@pytest.mark.parametrize("problem", [None, "missing", "duplicate"])
def test_plan_requires_complete_pinned_dual_distro_images(tmp_path, problem):
    images = build_images()
    if problem == "missing":
        images = [image for image in images if (image["target"], image["ros_distro"]) != ("api", "jazzy")]
    elif problem == "duplicate":
        images.append(dict(images[0]))
    result, output = write_plan(tmp_path, images=images)
    if problem:
        assert result.returncode != 0 and problem in result.stderr
        return
    assert result.returncode == 0, result.stderr
    plan = json.loads(output.read_text())
    context = plan["releaseContext"]
    expected = set(json.loads((ROOT / "openadkit.json").read_text())["componentImages"].values())
    assert set(context["images"]) == {"humble", "jazzy"}
    for distro, refs in context["images"].items():
        assert set(refs) == expected
        assert all(ref.endswith(f"@{DIGEST}") and f"-{distro}-{VERSION}@" in ref for ref in refs.values())
    assert {row["rosDistro"] for row in plan["bundle"]["validation"]} == {"humble", "jazzy"}
    assert any(row["node"] for row in plan["bundle"]["validation"])


def manager_env(tmp_path, problem):
    """One asset is sufficient to exercise ownership, race and content guards."""
    asset = tmp_path / "bundle.tar.gz"
    asset.write_bytes(b"validated bundle")
    state = {"id": 42, "tag_name": VERSION, "target_commitish": RELEASE_SHA, "name": VERSION,
             "draft": True, "prerelease": False, "body": MARKER, "assets": [{"id": 101, "name": asset.name}]}
    (tmp_path / "release-notes.md").write_text(MARKER)
    (tmp_path / "release-assets.sha256").write_text(f"{hashlib.sha256(asset.read_bytes()).hexdigest()}  {asset.name}\n")
    (tmp_path / "release-plan.json").write_text(json.dumps({
        "schemaVersion": 1, "release": {"version": VERSION, "releaseSha": RELEASE_SHA,
                                       "stable": True, "publishLatestAliases": True},
        "githubAssets": [{"name": asset.name, "path": asset.name}],
    }))
    refreshed = dict(state)
    if problem == "unowned":
        state["body"] = "manual draft\n"
    elif problem == "source":
        refreshed["target_commitish"] = "f" * 40
    elif problem == "body":
        refreshed["body"] += "changed\n"
    (tmp_path / "listed.json").write_text(json.dumps([[state]]))
    (tmp_path / "refreshed.json").write_text(json.dumps(refreshed))
    downloaded = tmp_path / "downloaded"
    downloaded.write_bytes(b"tampered" if problem == "asset" else asset.read_bytes())
    log = tmp_path / "gh-calls"
    executable(tmp_path / "bin/gh", f'''#!/usr/bin/env python3
import json, sys
from pathlib import Path
args = " ".join(sys.argv[1:])
root = Path({str(tmp_path)!r})
with (root / "gh-calls").open("a") as output:
    output.write(args + "\\n")
if "/git/refs/tags/" in args:
    print(json.dumps({{"object": {{"type": "commit", "sha": {RELEASE_SHA!r}}}}}))
elif "--method PATCH" in args or "--method DELETE" in args:
    pass
elif "/releases/assets/" in args:
    sys.stdout.buffer.write((root / "downloaded").read_bytes())
elif "--paginate --slurp" in args:
    print((root / "listed.json").read_text())
elif "/releases/42" in args:
    print((root / "refreshed.json").read_text())
else:
    sys.exit("unexpected gh call: " + args)
''')
    return os.environ | {
        "PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "GITHUB_REPOSITORY": "example/repo",
        "GITHUB_OUTPUT": str(tmp_path / "output"), "RELEASE_ID": "42",
        "RELEASE_BODY_SHA256": hashlib.sha256(MARKER.encode()).hexdigest(),
    }, log


@pytest.mark.parametrize(("operation", "problem"), [
    ("prepare", "unowned"), ("prepare", "source"),
    ("publish", "body"), ("publish", "asset"), ("publish", None),
])
def test_release_manager_revalidates_before_mutation(tmp_path, operation, problem):
    env, log = manager_env(tmp_path, problem)
    result = subprocess.run(["bash", str(ROOT / ".github/scripts/manage_github_release.sh"), operation],
                            cwd=tmp_path, env=env, text=True, capture_output=True, timeout=30)
    assert (result.returncode == 0) is (problem is None), result.stderr
    mutations = [call for call in log.read_text().splitlines() if "--method" in call]
    if problem:
        assert mutations == []
    else:
        assert len(mutations) == 1 and "releases/42" in mutations[0] and "draft=false" in mutations[0]


@pytest.mark.parametrize("problem", [None, "source", "conflict", "create", "policy"])
def test_promotion_never_updates_aliases_after_preflight_or_version_failure(tmp_path, problem):
    repo = "ghcr.io/example/openadkit"
    release_ref, alias = f"{repo}:api-humble-{VERSION}", f"{repo}:api-humble"
    (tmp_path / "release-plan.json").write_text(json.dumps({
        "schemaVersion": 1, "release": {"version": VERSION, "defaultRosDistro": "humble",
                                       "stable": True, "publishLatestAliases": True},
        "images": [{"repo": repo, "rosDistro": "humble", "digest": DIGEST,
                    "sourceRef": f"{repo}:api-humble-{BUILD_TAG}", "releaseRef": release_ref, "aliases": [alias]}],
    }))
    calls = tmp_path / "created"
    executable(tmp_path / "bin/docker", f'''#!/usr/bin/env python3
import json, sys
from pathlib import Path
args = sys.argv[1:]
created = Path({str(calls)!r})
if args[:3] == ["buildx", "imagetools", "inspect"]:
    ref = args[3]
    if {problem!r} == "conflict" and ref == {release_ref!r}:
        print(json.dumps({{"manifest": {{"digest": "sha256:" + "f" * 64}}}}))
    elif ref.endswith({BUILD_TAG!r}) or (created.exists() and ref in created.read_text().splitlines()):
        digest = "sha256:" + "f" * 64 if {problem!r} == "source" else {DIGEST!r}
        print(json.dumps({{"manifest": {{"digest": digest}}}}))
    else:
        sys.exit("ERROR: " + ref + ": not found")
elif args[:3] == ["buildx", "imagetools", "create"]:
    if {problem!r} == "create":
        sys.exit("create failed")
    with created.open("a") as output:
        output.write(args[4] + "\\n")
else:
    sys.exit("unexpected docker call")
''')
    executable(tmp_path / "bin/gh", f"#!/usr/bin/env bash\nprintf '%s\\n' {'v9.9.0' if problem == 'policy' else VERSION}\n")
    executable(tmp_path / "bin/sleep", "#!/usr/bin/env bash\nexit 0\n")
    result = subprocess.run(["bash", str(ROOT / ".github/scripts/promote_release_images.sh")],
                            cwd=tmp_path, text=True, capture_output=True, timeout=30, env=os.environ | {
                                "PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "GITHUB_REPOSITORY": "example/repo",
                                "REGISTRY_LOOKUP_MAX_ATTEMPTS": "1", "REGISTRY_LOOKUP_RETRY_DELAY_SECONDS": "0",
                            })
    assert (result.returncode == 0) is (problem is None), result.stderr
    assert (calls.read_text().splitlines() if calls.exists() else []) == ([] if problem else [release_ref, alias])
    if problem:
        assert {"source": "Source digest mismatch", "conflict": "Release tag conflict",
                "create": "did not converge", "policy": "Latest alias policy changed"}[problem] in result.stderr


def test_bundle_pins_integrity_and_reproducibility(tmp_path):
    env, calls = packager_env(tmp_path)
    run_packager(tmp_path, env)
    asset = tmp_path / f"dist/openadkit-{VERSION}.tar.gz"
    first_asset = hashlib.sha256(asset.read_bytes()).hexdigest()
    first_plan = (tmp_path / "release-plan.json").read_bytes()
    with tarfile.open(asset) as archive:
        members = archive.getmembers()
        assert members and all(member.mtime == 0 and member.uid == 0 and member.gid == 0 for member in members)
        assert all(not member.issym() and not member.islnk() for member in members)
        assert all("__pycache__" not in member.name and not member.name.endswith(".pyc") for member in members)
        archive.extractall(tmp_path / "extract", filter="data")
    root = tmp_path / f"extract/openadkit-{VERSION}"
    assert (root / "openadkit").read_bytes() == (ROOT / "openadkit").read_bytes()
    assert (tmp_path / "dist/openadkit").read_bytes() == (ROOT / "openadkit").read_bytes()
    context = json.loads((root / "openadkit.json").read_text())
    assert context["kind"] == "release" and set(context["images"]) == {"humble", "jazzy"}
    listed = subprocess.run([str(root / "openadkit"), "list"], env=env, text=True, capture_output=True, check=True)
    assert [line.split()[1] for line in listed.stdout.splitlines()[1:] if line.strip()] == ["intact"] * len(context["deployments"])
    assert "humble|" in calls.read_text() and "jazzy|" in calls.read_text()
    (tmp_path / "dist/stale.tar.gz").write_bytes(b"stale")
    run_packager(tmp_path, env, umask="077")
    assert hashlib.sha256(asset.read_bytes()).hexdigest() == first_asset
    assert (tmp_path / "release-plan.json").read_bytes() == first_plan
    assert sorted(path.name for path in (tmp_path / "dist").iterdir()) == ["openadkit", asset.name]
    scan = tmp_path / "release-input/scan"
    scan.mkdir()
    (scan / "scan-metadata.json").write_text('{"scan_status":"passed"}')
    subprocess.run(["bash", str(WRITE_NOTES)], cwd=tmp_path, env=env, check=True, capture_output=True)
    metadata = json.loads((tmp_path / "release-metadata.json").read_text())
    assert metadata["bundles"] == [{"name": asset.name, "sha256": first_asset}]
    assert metadata["release_plan_sha256"] == hashlib.sha256(first_plan).hexdigest()
    assert metadata["evidence"]["result"] == "PASSED"
