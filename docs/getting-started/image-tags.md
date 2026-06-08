# Container Image Tags

Open AD Kit publishes images to the GitHub Container Registry (`ghcr.io/autowarefoundation/openadkit`). Understanding the tag schema helps you choose the right level of stability and pinning for your deployment.

## Tag Reference

| Tag Pattern | Example | Description |
|---|---|---|
| **Stable release** | `planning-control-humble-v1.0.0` | Immutable release tag. Use this when you need a fully reproducible deployment. |
| **Latest stable alias** | `planning-control-humble` | Always resolves to the latest stable release for the specified ROS distro. |
| **Latest stable + suffix** | `planning-control-humble-latest` | Same as above, explicit. |
| **Default ROS distro alias** | `planning-control` | Convenience alias that resolves to the current default ROS distro (Humble). |
| **Default + latest suffix** | `planning-control-latest` | Explicit default-distro latest alias. |
| **Immutable build tag** | `planning-control-humble-123456789-1` | Pin to a specific CI build. Format is `<target>-<ros_distro>-<run_id>-<run_attempt>`. |
| **CI development alias** | `planning-control-amd64-humble` | Per-platform mutable tag used during CI. **Do not use for pinned deployments.** |
| **Pre-release** | `planning-control-humble-v1.0.0-rc.1` | Pre-release tag for testing. Pre-releases do not update latest stable aliases. |

## CUDA Images

CUDA-enabled variants follow the same patterns but are **amd64-only**:

| Tag Pattern | Example |
|---|---|
| Stable release | `sensing-perception-cuda-humble-v1.0.0` |
| Latest alias | `sensing-perception-cuda-humble` |

## Common Prefix

All component images share the same repository prefix:

```
ghcr.io/autowarefoundation/openadkit
```

## Choosing a Tag

- **Production / reproducible deployments**: Use a stable release tag (`vX.Y.Z`).
- **Development / latest features**: Use a latest stable alias (`<target>-<ros_distro>`).
- **Quick start / samples**: Use a default ROS distro alias (`<target>`).
- **Never pin to CI development aliases** (`amd64-*`) in committed deployment files — they are mutable and platform-specific.
