# Build from Source

How to build the Open AD Kit images locally and how CI builds them. Most users
do not need this: `openadkit run` pulls the published images (see
[Container Images & Versioning](../getting-started/container-images.md)).

## Prerequisites

- Ubuntu 22.04 or 24.04 (`openadkit setup` supports Ubuntu only; elsewhere,
  install Docker with Buildx and Compose yourself)
- Git, `pipx`, `vcs2l`, and `python3-yaml` to import the Autoware sources
- Disk space for several multi-gigabyte images

The component Dockerfiles build on upstream Autoware images from GHCR and
compile their package sets from a local `autoware/src` tree (step 4 below).

## Build System

Images are built with [Docker Bake](https://docs.docker.com/build/bake/) from
[`components/docker-bake.hcl`](https://github.com/autowarefoundation/openadkit/blob/main/components/docker-bake.hcl),
the same file CI uses.

--8<-- "includes/build-pipeline.md"

`universe-common` compiles the shared part of Autoware Universe on the upstream
`core-devel` image and copies the result onto the lean upstream `base` image, so
build tools never reach the runtime layers. Every component builds from it.
The CUDA variants, `sensing-perception-cuda` and `planning-cuda`, build on the
upstream CUDA images and add the `universe-common` install tree.

The published images end with a per-build Ubuntu security refresh. Components
compile on `universe-common-build`, the devel image without that refresh, which
CI pushes only to its build cache. Its digest changes only with its inputs, so a
build that changes no Autoware source or component Dockerfile reuses the cached
compiles and only refreshes and reassembles the runtime images.

| Group | Targets |
|-------|---------|
| `universe-common` | `universe-common-devel`, `universe-common` |
| `component` | all component images, including the amd64-only `sensing-perception-cuda` and `planning-cuda` |
| `planning-simulation` | `universe-common` plus the images Planning Simulation needs (local builds) |
| `default` | `universe-common` + `component` |

CI publishes every image to `{{ registry }}`.

## Build and Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/autowarefoundation/openadkit.git
cd openadkit

# 2. Install host dependencies
./openadkit setup --verify
```

--8<-- "includes/docker-group-activation.md"

```bash
# 3. Make the pipx-installed vcs command available in this shell
export PATH="$HOME/.local/bin:$PATH"

# 4. Import the Autoware sources this branch pins
AUTOWARE_REF=$(cat .github/autoware.ref)
git init autoware
git -C autoware fetch --depth 1 \
  https://github.com/autowarefoundation/autoware.git "$AUTOWARE_REF"
git -C autoware checkout --detach FETCH_HEAD
# An Autoware release, built on its official images
python3 .github/scripts/export_autoware_lock.py \
  autoware/repositories/autoware.repos autoware.lock
export UPSTREAM_TAG="$AUTOWARE_REF"
mkdir -p autoware/src
vcs import --shallow autoware/src < autoware.lock
mkdir -p autoware/src/middleware/external
touch autoware/src/middleware/external/.keep

# 5. Build the shared universe-common layer (~2 hours)
docker buildx bake -f components/docker-bake.hcl universe-common

# 6. Build the Planning Simulation images (~2 hours)
docker buildx bake -f components/docker-bake.hcl --load planning-simulation

# 7. Run with the local images
./openadkit run planning-simulation
```

- `--load` puts the images in the local Docker store; without it, Bake only
  fills the build cache.
- Local builds are tagged `<target>-<arch>-<ros-distro>` (for example
  `planning-amd64-humble`), which is the tag `./openadkit` looks up in a
  source checkout. The arch follows the build host; when cross-building, set tags
  with `--set <target>.tags=...`. To use other images, set the `*_IMAGE`
  variables in `~/.config/openadkit/<deployment>.env`.
- For Jazzy, build with `ROS_DISTRO=jazzy` and run with `--ros-distro jazzy`.

Other useful targets:

```bash
docker buildx bake -f components/docker-bake.hcl                                # everything
docker buildx bake -f components/docker-bake.hcl component                      # all components
docker buildx bake -f components/docker-bake.hcl --load sensing-perception      # one image
```

### Build Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROS_DISTRO` | `humble` or `jazzy` | `humble` |
| `UPSTREAM_TAG` | Upstream Autoware release to build on, the tag in `.github/autoware.ref` (e.g. `2.0.0`); required | `""` |
| `UPSTREAM_REPO` | Upstream Autoware image repository | `ghcr.io/autowarefoundation/autoware` |
| `ROS_SNAPSHOT_HUMBLE`, `ROS_SNAPSHOT_JAZZY` | ROS apt snapshot the `UPSTREAM_TAG` images were built from. The build fails when they do not match; see [ROS snapshot](https://github.com/autowarefoundation/openadkit/blob/main/components/shared/ros-snapshot/README.md). | Snapshots for `2.0.0` |

## Continuous Integration

[`build-all-images.yaml`](https://github.com/autowarefoundation/openadkit/blob/main/.github/workflows/build-all-images.yaml)
builds every target with the same Bake file. The build matrix comes from
[`.github/image-inventory.json`](https://github.com/autowarefoundation/openadkit/blob/main/.github/image-inventory.json),
the source of truth for which images are built and for which architectures.

Jobs run in dependency order: `prepare`, then `build-common`, then
`build-components`. Most images build for Humble and Jazzy on amd64 and arm64.
`create-manifests` then combines the per-arch images into multi-arch tags. CI disables the local tags (`LOCAL_IMAGE=""`) and tags
images through `docker/metadata-action`.

[`.github/autoware.ref`](https://github.com/autowarefoundation/openadkit/blob/main/.github/autoware.ref)
pins the Autoware release a branch builds on its official images. CI builds
`main` and `release/*` pushes, keeps registry caches per branch, and scans and
runs the evidence cells after each build. A weekly scan of `main`'s latest build
opens a GitHub issue when it fails.

A pull request builds only the images its changes affect; see
[Testing a Pull Request](evidence-workflow.md#testing-a-pull-request). Releases
promote one of these builds; see the [Release Process](release-process.md).
