# Logging Simulation

Replay a sample rosbag through sensing, perception and localization. An NVIDIA
GPU with at least 4 GB of VRAM is recommended; CPU mode works but is much
slower.

Complete the [Quickstart](../../getting-started/index.md) setup first. For GPU
mode, run `openadkit setup --gpu --verify`.

## Run

```bash
openadkit run logging-simulation         # CPU: clustering-based detection
openadkit run logging-simulation --gpu   # GPU: CenterPoint on CUDA (amd64 only)
```

--8<-- "includes/ros-distro.md"

`run` downloads the sample map and rosbag, and with `--gpu` also the CenterPoint
models (to `~/autoware_data/lidar_centerpoint`). The rosbag starts playing once
sensing subscribes to its LiDAR topic.

`run` returns once the services have started and stay up. This deployment
declares no readiness check of Autoware itself and is
[exempt from CI evidence](../../releases/evidence.md#ci-exemptions), so watch
`openadkit status` and the visualizer for localization to initialize.

The sample rosbag is Copyright 2020 TIER IV, Inc. It has no camera images, so
traffic-light recognition is unavailable and detection is less complete than
with a full recording.

## Open the Visualizer

--8<-- "includes/visualizer-remote-access.md"

## Stop and Recover

```bash
openadkit stop
```

To replace missing sample data, run `openadkit fetch logging-simulation --force`;
it also refreshes the CenterPoint models. For other issues, see
[Troubleshooting](../../getting-started/troubleshooting.md).
