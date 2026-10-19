"""main's weekly Autoware snapshot and the pin rules of resolve_build_inputs.sh."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".github/scripts"))

import bump_autoware  # noqa: E402

OLD, NEW = "a" * 40, "b" * 40
UNIVERSE = "https://github.com/autowarefoundation/autoware_universe.git"


def lock(**versions):
    lines = ["repositories:"]
    for path, version in versions.items():
        lines += [f'  "{path}":', '    type: "git"', f'    url: "{UNIVERSE}"', f'    version: "{version}"']
    return "\n".join(lines) + "\n"


def test_body_links_every_moved_repository_and_skips_unchanged_ones():
    body = bump_autoware.render_body(
        OLD, NEW,
        lock(universe=OLD, launcher=OLD, removed=OLD),
        lock(universe=NEW, launcher=OLD, added=NEW),
    )
    assert f"https://github.com/autowarefoundation/autoware/compare/{OLD}...{NEW}" in body
    assert f"| `universe` | [`{OLD[:12]}...{NEW[:12]}`](https://github.com/autowarefoundation/autoware_universe/compare/{OLD}...{NEW}) |" in body
    assert f"| `added` | added at `{NEW[:12]}` |" in body
    assert "| `removed` | removed |" in body
    assert "`launcher`" not in body


def test_body_from_a_release_pin_links_the_new_commit():
    body = bump_autoware.render_body("1.9.0", NEW, "", lock(universe=NEW))
    assert f"`1.9.0` → [`{NEW[:12]}`](https://github.com/autowarefoundation/autoware/commit/{NEW})" in body


def run_bump(tmp_path, monkeypatch, ref, current_lock, upstream_lock, base_ref=None):
    ref_file, lock_file = tmp_path / "autoware.ref", tmp_path / "autoware-lock.repos"
    ref_file.write_text(ref + "\n")
    if current_lock is not None:
        lock_file.write_text(current_lock)
    monkeypatch.setattr(bump_autoware, "upstream_head", lambda branch: NEW)
    # A release pin is compared with its own manifest, here universe at OLD.
    monkeypatch.setattr(bump_autoware, "export_snapshot",
                        lambda ref, development=True: upstream_lock if development else lock(universe=OLD))
    output, body = tmp_path / "output", tmp_path / "body.md"
    argv = ["--ref-file", str(ref_file), "--lock-file", str(lock_file), "--body", str(body), "--github-output", str(output)]
    if base_ref is not None:
        base = tmp_path / "base.ref"
        base.write_text(base_ref + "\n")
        argv += ["--base-ref-file", str(base), "--base-lock-file", str(tmp_path / "missing.repos")]
    assert bump_autoware.main(argv) == 0
    return ref_file, lock_file, output.read_text(), body.read_text()


def test_bump_writes_the_new_snapshot(tmp_path, monkeypatch):
    ref_file, lock_file, output, _ = run_bump(tmp_path, monkeypatch, "1.9.0", None, lock(universe=NEW))
    assert ref_file.read_text() == NEW + "\n"
    assert lock_file.read_text() == lock(universe=NEW)
    assert output == f"changed=true\nautoware_ref={NEW}\n"


def test_bump_from_a_release_compares_with_that_release(tmp_path, monkeypatch):
    *_, body = run_bump(tmp_path, monkeypatch, "1.9.0", None, lock(universe=NEW))
    assert f"| `universe` | [`{OLD[:12]}...{NEW[:12]}`]" in body
    assert "added at" not in body


def test_bump_leaves_a_current_snapshot_alone(tmp_path, monkeypatch):
    current = lock(universe=NEW)
    _, lock_file, output, _ = run_bump(tmp_path, monkeypatch, NEW, current, current)
    assert lock_file.read_text() == current
    assert output.startswith("changed=false\n")


def test_bump_describes_the_pull_request_against_its_base(tmp_path, monkeypatch):
    # A rerun on an open bump compares with main, not with last week's bump.
    *_, body = run_bump(tmp_path, monkeypatch, OLD, lock(universe=OLD), lock(universe=NEW), base_ref="1.9.0")
    assert "`1.9.0` →" in body


FAKE_GIT = r"""#!/usr/bin/env bash
# Answers resolve_build_inputs.sh's git calls for one Autoware ref.
args=("$@")
[ "${args[0]}" = -C ] && args=("${args[@]:2}")
case "${args[0]}" in
  init|remote|checkout) exit 0 ;;
  ls-remote)
    case "${args[*]}" in
      *refs/heads/"${FAKE_BRANCH:-}") [ -n "${FAKE_BRANCH:-}" ] && echo "${FAKE_SHA} x" && exit 0 ;;
      *refs/tags/"${FAKE_TAG:-}") [ -n "${FAKE_TAG:-}" ] && echo "${FAKE_SHA} x" && exit 0 ;;
    esac
    exit 2 ;;
  fetch) mkdir -p autoware-metadata/repositories && touch autoware-metadata/repositories/autoware-nightly.repos ;;
  rev-parse) echo "${FAKE_SHA}" ;;
  describe) echo 1.9.0 ;;
esac
"""


def resolve(tmp_path, pin, *, lock_file=False, ref_name="main", **fake):
    work = tmp_path / "work"
    (work / ".github").mkdir(parents=True)
    (work / ".github/autoware.ref").write_text(pin + "\n")
    if lock_file:
        (work / ".github/autoware-lock.repos").write_text(lock(universe=NEW))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "git").write_text(FAKE_GIT)
    (bin_dir / "git").chmod(0o755)
    output = tmp_path / "github-output"
    env = os.environ | {
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "GITHUB_OUTPUT": str(output), "GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_EVENT_NAME": "push", "GITHUB_REF_NAME": ref_name, "FAKE_SHA": NEW,
        **fake,
    }
    env.pop("GITHUB_BASE_REF", None)
    result = subprocess.run(
        ["bash", str(ROOT / ".github/scripts/resolve_build_inputs.sh")],
        cwd=work, env=env, capture_output=True, text=True,
    )
    values = dict(line.split("=", 1) for line in output.read_text().splitlines()) if output.exists() else {}
    return result, values


def test_a_commit_pin_builds_its_committed_lock(tmp_path):
    result, values = resolve(tmp_path, NEW, lock_file=True)
    assert result.returncode == 0, result.stderr
    assert values["autoware_ref_type"] == "sha"
    assert values["autoware_lock_file"] == ".github/autoware-lock.repos"
    assert values["autoware_overlay"] == ""
    assert values["upstream_tag"] == ""


def test_a_commit_pin_without_its_lock_fails(tmp_path):
    result, _ = resolve(tmp_path, NEW)
    assert result.returncode != 0
    assert "needs its dependency lock" in result.stderr


def test_a_release_pin_uses_the_release_manifest(tmp_path):
    result, values = resolve(tmp_path, "1.9.0", FAKE_TAG="1.9.0")
    assert result.returncode == 0, result.stderr
    assert values["autoware_ref_type"] == "tag"
    assert values["upstream_tag"] == "1.9.0"
    assert values["autoware_lock_file"] == ""


def test_a_release_pin_rejects_an_inherited_development_lock(tmp_path):
    result, _ = resolve(tmp_path, "1.9.0", lock_file=True, FAKE_TAG="1.9.0")
    assert result.returncode != 0
    assert "remove .github/autoware-lock.repos" in result.stderr


def test_a_branch_pin_resolves_the_development_manifest(tmp_path):
    result, values = resolve(tmp_path, "main", FAKE_BRANCH="main")
    assert result.returncode == 0, result.stderr
    assert values["autoware_ref_type"] == "branch"
    assert values["autoware_overlay"].endswith("autoware-nightly.repos")


@pytest.mark.parametrize(("ref_name", "scope"), [("ci/bump-autoware", "main"), ("release/2.0", "release-2.0"), ("main", "main")])
def test_the_bump_shares_mains_caches(tmp_path, ref_name, scope):
    result, values = resolve(tmp_path, NEW, lock_file=True, ref_name=ref_name)
    assert result.returncode == 0, result.stderr
    assert values["cache_scope"] == scope
