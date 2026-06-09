#!/usr/bin/env python3
"""Generate docs/releases/index.md from GitHub Releases."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = "autowarefoundation/openadkit"
GITHUB_RELEASES_URL = f"https://api.github.com/repos/{REPO}/releases"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "releases" / "index.md"


def parse_args() -> tuple[str, Path]:
    parser = argparse.ArgumentParser(
        description="Generate docs/releases/index.md from GitHub Releases.",
        epilog="If GITHUB_TOKEN is set in the environment, it is used for API requests."
    )
    parser.add_argument(
        "--repo",
        default="autowarefoundation/openadkit",
        help="GitHub repository in 'owner/name' format (default: %(default)s)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: <script-dir>/../releases/index.md)"
    )
    args = parser.parse_args()
    output_path = args.output or Path(__file__).resolve().parent.parent / "releases" / "index.md"
    return args.repo, output_path


def fetch_releases(token: Optional[str]) -> list[dict]:
    releases: list[dict] = []
    page = 1

    while True:
        url = f"{GITHUB_RELEASES_URL}?{urllib.parse.urlencode({'per_page': 100, 'page': page})}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "openadkit-docs-release-notes-generator",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                batch = json.load(response)
        except urllib.error.HTTPError as exc:
            print(f"GitHub API request failed: {exc.code} {exc.reason}", file=sys.stderr)
            raise SystemExit(1) from exc
        except urllib.error.URLError as exc:
            print(f"GitHub API request failed: {exc.reason}", file=sys.stderr)
            raise SystemExit(1) from exc

        if not batch:
            break

        releases.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return releases


def format_date(iso_timestamp: str) -> str:
    parsed = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d")


def release_badges(release: dict) -> str:
    badges: list[str] = []
    if release.get("prerelease"):
        badges.append("Pre-release")
    if release.get("draft"):
        badges.append("Draft")
    if not release.get("prerelease") and not release.get("draft"):
        badges.append("Stable")
    return " · ".join(badges)


def render_empty_state() -> str:
    return "\n".join(
        [
            "# Releases",
            "",
            "Published Open AD Kit releases are listed here, synchronized from",
            f"[GitHub Releases](https://github.com/{REPO}/releases).",
            "",
            "!!! info \"No releases yet\"",
            "    There are no published releases yet. While waiting for the first stable release, you can:",
            "",
            "    - Pull images from [GitHub Container Registry](https://github.com/autowarefoundation/openadkit/pkgs/container/openadkit)",
            "    - Use CI build tags as described in [Container Image Tags](../getting-started/image-tags.md)",
            "    - Read how maintainers promote builds in [Release Flow](../getting-started/release-flow.md)",
            "    - [Watch releases on GitHub](https://github.com/autowarefoundation/openadkit/releases) for notifications",
            "",
        ]
    )


def render_release_section(release: dict) -> str:
    tag = release.get("tag_name", "unknown")
    title = release.get("name") or f"Open AD Kit {tag}"
    published_at = release.get("published_at") or release.get("created_at") or ""
    published_date = format_date(published_at) if published_at else "unknown date"
    html_url = release.get("html_url", f"https://github.com/{REPO}/releases/tag/{tag}")
    body = (release.get("body") or "").strip()

    lines = [
        f"## {title}",
        "",
        f"**Published:** {published_date} · **Type:** {release_badges(release)} ·",
        f"[View on GitHub]({html_url})",
        "",
    ]

    if body:
        lines.append(body)
        lines.append("")

    return "\n".join(lines)


def render_release_notes(releases: list[dict]) -> str:
    published = [release for release in releases if not release.get("draft")]

    if not published:
        return render_empty_state()

    lines = [
        "# Releases",
        "",
        "Published Open AD Kit releases are listed here, synchronized from",
        f"[GitHub Releases](https://github.com/{REPO}/releases).",
        "",
    ]

    for release in published:
        lines.append(render_release_section(release))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    global REPO, GITHUB_RELEASES_URL, OUTPUT_PATH

    repo, output_path = parse_args()
    REPO = repo
    GITHUB_RELEASES_URL = f"https://api.github.com/repos/{REPO}/releases"
    OUTPUT_PATH = output_path

    token = os.environ.get("GITHUB_TOKEN")
    releases = fetch_releases(token)
    content = render_release_notes(releases)

    header = "<!-- AUTOGENERATED by generate_release_notes.py; DO NOT EDIT MANUALLY -->\n\n"

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(header + content, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(releases)} release(s) fetched)")


if __name__ == "__main__":
    main()
