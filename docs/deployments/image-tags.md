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
| Stable distro tag | `planning-control-humble` | Latest promoted release for a ROS distribution. Mutable. |
| Legacy Humble tag | `planning-control` | Compatibility tag for sample deployments. Equivalent to the latest promoted Humble release. Mutable. |
| Release tag | `planning-control-humble-v1.0.0` | Manually promoted immutable release tag. Recommended for pinned deployments. |
| Architecture build tag | `planning-control-amd64-humble-123456789-1` | Intermediate per-platform tag used to assemble multi-arch manifests. Not intended for deployments. |

## Recommended Usage

Use release tags when a deployment must be reproducible:

```yaml
image: ghcr.io/autowarefoundation/openadkit:planning-control-humble-v1.0.0
```

Use stable tags when you want the latest promoted release image for a ROS distribution:

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

The release workflow does not rebuild images. A successful `build-all-images` run from `main` creates immutable build tags, multi-architecture manifests, smoke-test results, and a release candidate manifest artifact containing every expected image digest. The scan workflow must pass for the exact same `build_tag`; critical and high vulnerability findings fail the scan gate.

Release promotion validates the source build, release candidate manifest, smoke-test result, scan summary, source labels, and destination tag conflicts. It promotes only the recorded source digests to release tags, verifies the promoted digests, and then creates or updates the GitHub release with the manifest and scan summary attached. Stable and legacy tags are moved only from the release workflow after successful release promotion.

If promotion fails partway through, rerun the same release workflow with the same `version` and `build_tag`. Existing release tags are accepted only when their digest matches the recorded release candidate digest; conflicting tags stop the release. Stable tags are mutable by design and may be rerun after release tags are fully verified.

Repository administrators should protect the `release` GitHub Environment with required reviewers before enabling production releases. The workflow references the environment, but reviewer rules are configured in repository settings.
