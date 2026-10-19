#!/usr/bin/env python3
"""Move main's Autoware development snapshot to the current upstream main.

main builds one committed snapshot of upstream development: the Autoware
commit in .github/autoware.ref and every dependency pinned to a commit in
.github/autoware-lock.repos. bump-autoware.yaml runs this weekly and proposes
the result as a pull request, so an upstream change that breaks Open AD Kit
fails that pull request instead of main.

Writes both files when the snapshot moved, a pull request body, and
`changed`/`autoware_ref` lines for $GITHUB_OUTPUT. Uses only the standard
library and PyYAML, like export_autoware_lock.py.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile
import urllib.request
from collections.abc import Callable

import yaml

from export_autoware_lock import SHA_RE, export_lock, ls_remote

AUTOWARE_URL = "https://github.com/autowarefoundation/autoware"
RAW_URL = "https://raw.githubusercontent.com/autowarefoundation/autoware"
# The release manifest, and upstream's development overlay that moves the
# listed repositories to their development branches.
MANIFESTS = ("repositories/autoware.repos", "repositories/autoware-nightly.repos")


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def upstream_head(branch: str, resolve: Callable[[str, str], str | None] = ls_remote) -> str:
    sha = resolve(AUTOWARE_URL, f"refs/heads/{branch}")
    if not sha or not SHA_RE.fullmatch(sha):
        raise RuntimeError(f"could not resolve Autoware {branch}")
    return sha.lower()


def export_snapshot(ref: str, fetch: Callable[[str], str] = fetch_text, *, development: bool = True) -> str:
    """The dependency lock of Autoware at ref, with its development overlay
    for a development snapshot, or as released for a release tag."""
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        paths = []
        for manifest in MANIFESTS if development else MANIFESTS[:1]:
            path = root / pathlib.PurePosixPath(manifest).name
            path.write_text(fetch(f"{RAW_URL}/{ref}/{manifest}"), encoding="utf-8")
            paths.append(path)
        target = root / "autoware-lock.repos"
        export_lock(paths[0], target, paths[1] if development else None)
        return target.read_text(encoding="utf-8")


def repositories(lock: str) -> dict[str, dict[str, str]]:
    return (yaml.safe_load(lock) or {}).get("repositories", {}) if lock else {}


def compare_url(url: str, old: str, new: str) -> str:
    return f"{url.removesuffix('.git')}/compare/{old}...{new}"


def render_body(old_ref: str, new_ref: str, old_lock: str, new_lock: str) -> str:
    """A pull request body listing what moved, with a compare link for each."""
    old, new = repositories(old_lock), repositories(new_lock)
    if SHA_RE.fullmatch(old_ref):
        autoware = f"[`{old_ref[:12]}...{new_ref[:12]}`]({compare_url(AUTOWARE_URL, old_ref, new_ref)})"
    else:
        autoware = f"`{old_ref}` → [`{new_ref[:12]}`]({AUTOWARE_URL}/commit/{new_ref})"
    rows = []
    for path in sorted(old.keys() | new.keys()):
        before, after = old.get(path), new.get(path)
        if before == after:
            continue
        if after is None:
            change = "removed"
        elif before is None:
            change = f"added at `{after['version'][:12]}`"
        elif before["url"] != after["url"]:
            change = f"moved to {after['url']} at `{after['version'][:12]}`"
        else:
            change = f"[`{before['version'][:12]}...{after['version'][:12]}`]({compare_url(after['url'], before['version'], after['version'])})"
        rows.append(f"| `{path}` | {change} |")
    lines = [
        "Moves `main` to the current Autoware development snapshot "
        "(`.github/autoware.ref`, `.github/autoware-lock.repos`).",
        "",
        f"Autoware: {autoware}",
        "",
    ]
    if rows:
        lines += ["| Repository | Change |", "| --- | --- |", *rows, ""]
    lines += [
        "bump-autoware.yaml builds every image on this branch and then runs "
        "the evidence cells; they report as the `bump-autoware / build` and "
        "`bump-autoware / evidence` statuses of this pull request. When "
        "upstream breaks a deployment, push the adaptation to this branch: "
        "the next weekly run moves the snapshot on top of it.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--branch", default="main", help="upstream Autoware branch to snapshot")
    parser.add_argument("--ref-file", type=pathlib.Path, default=pathlib.Path(".github/autoware.ref"))
    parser.add_argument("--lock-file", type=pathlib.Path, default=pathlib.Path(".github/autoware-lock.repos"))
    parser.add_argument("--base-ref-file", type=pathlib.Path, help="the pull request base's ref file (default: --ref-file)")
    parser.add_argument("--base-lock-file", type=pathlib.Path, help="the pull request base's lock (default: --lock-file)")
    parser.add_argument("--body", type=pathlib.Path, required=True, help="where to write the pull request body")
    parser.add_argument("--github-output", type=pathlib.Path, help="append changed=/autoware_ref= here")
    args = parser.parse_args(argv)

    def read(path: pathlib.Path) -> str:
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    old_ref = read(args.ref_file).strip()
    old_lock = read(args.lock_file)
    new_ref = upstream_head(args.branch)
    new_lock = export_snapshot(new_ref)
    changed = new_ref != old_ref or new_lock != old_lock
    if changed:
        args.ref_file.write_text(new_ref + "\n", encoding="utf-8")
        args.lock_file.write_text(new_lock, encoding="utf-8")
    # The body describes the whole pull request: the base's snapshot to the new one.
    base_ref = read(args.base_ref_file).strip() if args.base_ref_file else old_ref
    base_lock = read(args.base_lock_file) if args.base_lock_file else old_lock
    if not base_lock and base_ref and not SHA_RE.fullmatch(base_ref):
        # A release pin keeps no lock: compare with that release's manifest.
        base_lock = export_snapshot(base_ref, development=False)
    args.body.write_text(render_body(base_ref, new_ref, base_lock, new_lock), encoding="utf-8")
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"changed={'true' if changed else 'false'}\nautoware_ref={new_ref}\n")
    print(f"Autoware {args.branch}: {old_ref} -> {new_ref} ({'changed' if changed else 'unchanged'})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
