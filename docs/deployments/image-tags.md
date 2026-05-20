# Image Tags

Open AD Kit publishes container images to GitHub Container Registry using a small set of tag types. Use immutable release tags for reproducible deployments and stable tags for quick local evaluation.

## Registries

| Image family | Registry path |
|--------------|---------------|
| Common base and development images | `ghcr.io/autowarefoundation/openadkit-common` |
| Runtime component and universe images | `ghcr.io/autowarefoundation/openadkit` |

## Tag Types

| Tag type | Example | Purpose |
|----------|---------|---------|
| Immutable build tag | `planning-control-humble-123456789-1` | Exact output of a `build-all-images` workflow run. This is the source for release promotion. |
| Stable distro tag | `planning-control-humble` | Latest successful `main` build for a ROS distribution. Mutable. |
| Legacy Humble tag | `planning-control` | Compatibility tag for sample deployments. Equivalent to the latest successful Humble build on `main`. Mutable. |
| Release tag | `planning-control-humble-v1.0.0` | Manually promoted immutable release tag. Recommended for pinned deployments. |
| Architecture build tag | `planning-control-amd64-humble-123456789-1` | Intermediate per-platform tag used to assemble multi-arch manifests. Not intended for deployments. |

## Recommended Usage

Use release tags when a deployment must be reproducible:

```yaml
image: ghcr.io/autowarefoundation/openadkit:planning-control-humble-v1.0.0
```

Use stable tags when you want the latest successful image for a ROS distribution:

```yaml
image: ghcr.io/autowarefoundation/openadkit:planning-control-humble
```

The sample deployments use the legacy Humble tags for readability:

```yaml
image: ghcr.io/autowarefoundation/openadkit:planning-control
```

## CUDA Images

CUDA image tags use the same policy with a `-cuda` suffix, for example `sensing-perception-cuda-humble-v1.0.0`. CUDA images are currently published as amd64-only manifests.

## Release Promotion

The release workflow does not rebuild images. It validates a successful `build-all-images` run from `main`, verifies every expected source image exists and has matching provenance labels, rejects conflicting release image tags, promotes the build manifests to release tags, verifies the promoted images, and then creates the GitHub release. If a rerun finds an existing release image tag with the same digest as the source build image, it treats that image as already promoted.
