# Releases

--8<-- "includes/first-release-note.md"

[GitHub Releases](https://github.com/autowarefoundation/openadkit/releases) is
the canonical source for published versions, release notes and provenance
metadata. Each stable release publishes:

- a versionless `openadkit` installer
- the versioned `openadkit-vX.Y.Z.tar.gz` bundle: the CLI and the deployments
- `release-plan.json` and `release-metadata.json`: the pinned Autoware release,
  ROS 2 distros, image tags and digests, the BOM, the passing evidence summary
  and the CI exemptions
- build provenance for the installer, bundle, plan and metadata

The release notes open with the highlights and the install command, list the
merged pull requests by type, and summarize the evidence. An installed release
moves to the latest stable version with `openadkit upgrade`.

- [Container Images & Versioning](container-images.md) — image tags and what
  to pin
- [Compatibility](compatibility.md) — what a version number promises
- [Evidence Policy](evidence.md) — what a build must pass to be released
- [Verify a Release](verification.md) — check the files before you run them
