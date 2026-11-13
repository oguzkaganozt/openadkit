# Logging Simulation

Replay a sample rosbag through sensing, perception and localization. An NVIDIA
GPU with at least 4 GB of VRAM is recommended; CPU mode detects objects by
clustering instead of CenterPoint.

## Run

```bash
openadkit run logging-simulation         # CPU: clustering-based detection
openadkit run logging-simulation --gpu   # GPU: CenterPoint on CUDA (amd64 only)
```

`run` downloads the sample map and rosbag, and with `--gpu` also the CenterPoint
models (to `~/autoware_data/lidar_centerpoint`). The rosbag starts playing once
sensing subscribes to its LiDAR topic, at 0.4× speed (`ROSBAG_RATE`), and plays
once: `openadkit restart rosbag` plays it again.

`run` returns once the stack is ready: the services stay up and the AD API can
initialize localization. `openadkit run logging-simulation --verify` then
follows the replay: it passes once localization is initialized and the pose and
the tracked objects keep arriving. Every release runs that check in CPU mode;
the GPU mode is checked by hand on a GPU host.

The sample rosbag is Copyright 2020 TIER IV, Inc. It has no camera images, so
traffic-light recognition is unavailable and detection is less complete than
with a full recording.

## Stop and Recover

To replace missing sample data, run `openadkit fetch logging-simulation --force`;
it also refreshes the CenterPoint models. See [Stop and Recover](index.md#stop-and-recover) for the rest.
