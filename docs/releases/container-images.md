# Container Images & Versioning

Open AD Kit publishes images to the GitHub Container Registry (`{{ registry }}`).
This page is the reference for image tags, versions, and what "supported" means.

## Tag Reference

A release promotes an existing CI build instead of rebuilding it, so the
images tested in CI are the images that ship.

| Tag | Example | Created | Moves? |
|-----|---------|---------|--------|
| **Release** | `planning-humble-v2.0.0` | Every release | No |
| **Latest alias** | `planning-humble` | Stable releases | Yes |
| **Pre-release** | `planning-humble-v2.0.0-rc.1` | Pre-releases | No |
| **CI build** | `planning-humble-123456789-1` | Every CI build (`<run_id>-<run_attempt>`) | No |

Pre-releases never move the latest aliases. No alias leaves out the
distro, so an image never switches ROS distro under the same tag.

Examples use **{{ default_distro_title }}**, the default distro. Jazzy images use
the same patterns with `-jazzy` (for example `planning-jazzy`).
`sensing-perception-cuda` and `planning-cuda` are amd64-only, and only the amd64
`simulator` carries the CARLA client.

## Choosing a Tag

- **Reproducible deployments**: use a release tag (`vX.Y.Z`) or a digest.
- **Latest stable for a distro**: use `<target>-<ros_distro>`.
- **Never** pin per-architecture tags such as `universe-common-amd64-humble`:
  CI moves them with every build of `main`, and publishes them only for the
  common images its own builds start from.
- **Source checkout**: `./openadkit` runs `<target>-<arch>-<ros_distro>`, the
  tags of a [local build](../development/build-from-source.md), not published
  images.

## Versioning

Open AD Kit versions follow [Semantic Versioning](https://semver.org/) on their
own, starting at `v2.0.0`: a backward-incompatible change to the CLI, the
manifests or a deployment raises the major version, and a move to a new
Autoware release raises at least the minor version. The release notes list what
breaks, and [Compatibility](compatibility.md) lists what a major
version keeps working.

- **One Autoware release per release.** Releases come from `main`, which pins
  one Autoware release in `.github/autoware.ref`. The
  [GitHub Release](https://github.com/autowarefoundation/openadkit/releases)
  title pairs the two, `Open AD Kit v2.0.1 · Autoware 2.0.0`, and so do
  `openadkit install` and `openadkit version`.
- **Pinned inputs.** A release also pins the ROS distros and every image
  digest, and its images carry
  `org.opencontainers.image.autoware-base-version`.
- **Backports.** A fix that is upstream but not yet in an Autoware release can
  be [backported](../development/release-process.md#backporting-an-autoware-fix);
  the release notes list it, and the Autoware version stays the tag's.
- **Older versions.** A `release/X.Y` branch is created from a release tag only
  to fix an older version.

## ROS Distro Support

| Distro | Status |
|--------|--------|
| **Humble** | Default |
| **Jazzy** | Supported |

A release bundle pins images for both distros; choose one with `--ros-distro`.
A release needs the evidence cells of both distros to pass its
[gate](evidence.md), and a distro is supported only while it is
supported upstream. Changing the default takes a reviewed manifest change and
passing evidence; a release never falls back to another distro by itself.
Evidence runs on amd64 and arm64 hosts; the CUDA images, which are amd64-only,
are checked by hand.

### ROS Package Snapshot

Every image installs its ROS packages from one dated
[ROS snapshot](http://snapshots.ros.org/): the one the upstream Autoware images
of that release were built from. Compiled code and runtime therefore use the
same ROS versions, and the build fails if they would differ. The release BOM
names the snapshot per distro; an image carries it as a label:

```bash
docker inspect --format '{{ "{{" }} index .Config.Labels "org.opencontainers.image.ros-snapshot" {{ "}}" }}' \
  {{ registry }}:planning-humble
```

The snapshot changes only with the upstream Autoware release. Ubuntu packages
are not pinned, so security updates keep flowing into new builds.

## What "Supported" Means

- **Releases**: the latest stable release is supported. Fixes, including CVE
  remediation, ship in a new release; older releases are not patched.
- **Platforms**: a path is supported, experimental or unsupported. See
  [Supported Platforms](../platforms/index.md).
- **No certification claims**: Open AD Kit makes no safety-certification,
  functional-safety or production-readiness claim.

Community help and version coverage are described in
[SUPPORT.md](https://github.com/autowarefoundation/openadkit/blob/main/.github/SUPPORT.md);
report security vulnerabilities through the
[private reporting policy](https://github.com/autowarefoundation/openadkit/blob/main/.github/SECURITY.md).

Maintainers: see the [Release Process](../development/release-process.md).
