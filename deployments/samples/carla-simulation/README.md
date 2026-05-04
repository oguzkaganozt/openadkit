# Autoware Open AD Kit CARLA Simulation

This sample deployment runs the existing Open AD Kit planning stack with CARLA as an external world source.

## Requirements

- Docker Compose (v2)
- A compatible CARLA image host runtime and container image access
- Optional: NVIDIA runtime for GPU acceleration (recommended for CARLA rendering)

If you do not enable GPU passthrough, set `CARLA_RENDERING=-RenderOffScreen` (already default).

## Start the deployment

1. Start services:

   ```bash
   docker compose --env-file carla-simulation.env up -d
   ```

2. Open RViz:

   ```
   http://localhost:6080/vnc.html
   ```

   Password: `openadkit`

3. After RViz starts, use `2D Pose Estimate` to seed the ego pose and start your route flow.

## Runtime checks

- Confirm ROS graph topics show bridge outputs:

  ```bash
  docker exec -it autoware-map ros2 topic list | grep -E 'clock|control|sensing|vehicle'
  ```

- Ensure `/clock` is active and `use_sim_time=true` in simulator and core components.

- Confirm no dummy world feeds are enabled by checking startup logs for:
  `LAUNCH_DUMMY_VEHICLE=false`, `LAUNCH_DUMMY_PERCEPTION=false`, `LAUNCH_DUMMY_DOORS=false`.

## Topic integration contract

CARLA bridge topic names and remaps are controlled by:

`CARLA_ROS_BRIDGE_REMAP_FILE` (defaults to `./carla_bridge_remap.camera_lidar.args`).
`CARLA_SYNCHRONOUS_MODE` is optional: set it only when your selected bridge launch file supports the `synchronous_mode` argument.

- Vehicle command path expected by Autoware (default examples):
  - `/carla/ego_vehicle/vehicle_control_cmd -> /control/command/control_cmd`
  - `/carla/ego_vehicle/vehicle_status -> /vehicle/status/velocity_status`
- Sensor paths expected by Autoware perception (default examples):
  - `/sensing/lidar/top/pointcloud_raw` (`sensor_msgs/msg/PointCloud2`)
  - `/sensing/imu/imu_data` (`sensor_msgs/msg/Imu`)
  - `/sensing/gnss/pose` (`geometry_msgs/msg/PoseWithCovarianceStamped`)
- TF / time alignment:
  - `/clock` should be remapped from CARLA to `/clock`.
  - `/tf` and `/tf_static` must stay consistent for base frame and map frame alignment.
  - `USE_SIM_TIME=true` and `SCENARIO_SIMULATION=true` are enabled by default.

If your CARLA topic role names differ, update `carla_bridge_remap.camera_lidar.args` and set `CARLA_ROS_BRIDGE_REMAP_FILE` accordingly.

## Camera + lidar vs lidar-only bridge

- Camera+lidar mode: default remap file
  - `CARLA_ROS_BRIDGE_REMAP_FILE=./carla_bridge_remap.camera_lidar.args`
- LiDAR-only mode: use the lidar-only template
  1. Edit `carla-simulation.env` and set:
     ```bash
     CARLA_ROS_BRIDGE_REMAP_FILE=./carla_bridge_remap.lidar_only.args
     ```
  2. Restart the bridge:
     ```bash
     docker compose --env-file carla-simulation.env up -d carla-ros-bridge
     ```

## Stop

```bash
docker compose --env-file carla-simulation.env down
```
