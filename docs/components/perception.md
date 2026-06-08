# Perception

The perception component processes sensor data to create an understanding of the environment. It includes:

- **Object detection** — Multi-class detection using camera, LiDAR, and radar fusion
- **Object tracking** — Multi-Object Tracking v2 for temporal consistency
- **Priority Object Merger** — Resolution of overlapping detections
- **Camera-Only 3D Detection** — Monocular depth estimation
- **Radar-Only 3D Detection** — Radar-based object localization
- **Cluster-Based 3D Detection** — Unsupervised LiDAR clustering

For more details, see the [Autoware perception design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture-v1/components/perception/).
