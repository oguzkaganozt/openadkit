# Releases

**No stable release has been published yet.** Until the first release, run Open
AD Kit from a [source checkout](../getting-started/index.md).

[GitHub Releases](https://github.com/autowarefoundation/openadkit/releases) is
the canonical source for published versions, release notes, and provenance
metadata. Each stable release publishes:

- a versionless `openadkit` installer
- the versioned `openadkit-vX.Y.Z.tar.gz` bundle
- the pinned Autoware meta-release, ROS 2 distro(s), and image tags and digests
- a BOM, the passing runtime evidence summary, explicit CI exemptions and default distro
- build provenance for the installer, bundle, plan and metadata

Installed releases move to the latest stable version with `openadkit upgrade`.
Tag naming is documented in
[Container Images & Versioning](../getting-started/container-images.md).
See [Evidence Policy](evidence.md) for the blocking gate and verification report, and
[Verify a Release](verification.md) before executing downloaded artifacts.

Planned work and its priority order are on the [Roadmap](../roadmap.md).
