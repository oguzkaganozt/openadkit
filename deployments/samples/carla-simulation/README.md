# Autoware Open AD Kit CARLA Simulation

This sample deployment runs the existing Open AD Kit planning stack with CARLA as an external world source.

## Requirements

- Docker Compose (v2)
- A compatible CARLA image host runtime and container image access
- Optional: NVIDIA runtime for GPU acceleration (recommended for CARLA rendering)

If you do not enable GPU passthrough, set `CARLA_RENDERING=-RenderOffScreen` (already default).

## Start the deployment

1. Build the local CARLA ROS bridge image:

   ```bash
   git clone --recurse-submodules https://github.com/carla-simulator/ros-bridge.git ~/carla-ros-bridge
   cp Dockerfile.carla-ros-bridge.humble ~/carla-ros-bridge/Dockerfile.openadkit
   docker build \
     --build-arg CARLA_VERSION=0.9.15 \
     --build-arg ROS_DISTRO=humble \
     -t local/carla-ros-bridge:0.9.15-humble \
     -f ~/carla-ros-bridge/Dockerfile.openadkit \
     ~/carla-ros-bridge
   ```

   If the VM cannot reach the default Ubuntu apt mirrors reliably, pass a regional mirror:

   ```bash
   docker build \
     --build-arg CARLA_VERSION=0.9.15 \
     --build-arg ROS_DISTRO=humble \
     --build-arg UBUNTU_APT_MIRROR=http://es.archive.ubuntu.com/ubuntu \
     --build-arg UBUNTU_SECURITY_APT_MIRROR=http://es.archive.ubuntu.com/ubuntu \
     -t local/carla-ros-bridge:0.9.15-humble \
     -f ~/carla-ros-bridge/Dockerfile.openadkit \
     ~/carla-ros-bridge
   ```

2. Start services with the startup helper.

   For a reproducible RViz planning demo, use planning demo mode:

   ```bash
   ./start-carla-simulation.sh --planning-demo
   ```

   This mode starts CARLA and the CARLA ROS bridge for visualization and sensor topics, while Autoware uses dummy vehicle and perception publishers so `2D Pose Estimate`, `2D Goal Pose`, `Auto`, and `Accept Start` work in RViz without CARLA adapter nodes. It also uses a bridge launch path that does not subscribe to RViz `/initialpose`, avoiding a collision with Autoware's pose initialization. A demo-only MRM suppressor is enabled because the full fail-safe graph can briefly report stale diagnostics when running this mixed CARLA/dummy setup.

   For adapter development mode, where dummy vehicle and dummy perception remain disabled, run:

   ```bash
   ./start-carla-simulation.sh
   ```

   The helper starts CARLA first, waits for the RPC port, recreates the bridge, waits for CARLA objects to spawn, starts the remaining OpenADKit services, and verifies `/clock` plus key topics.

   To run without the GPU override:

   ```bash
   ./start-carla-simulation.sh --no-gpu
   ```

3. Open RViz:

   ```
   http://localhost:6080/vnc.html
   ```

   Password: `openadkit`

4. In planning demo mode, after RViz starts:

   - Use `2D Pose Estimate` to seed the ego pose.
   - Use `2D Goal Pose` to set a route.
   - Click `Auto`.
   - Click `Accept Start` if prompted.

## Runtime checks

- Confirm ROS graph topics show bridge outputs:

  ```bash
  docker exec -it autoware-map ros2 topic list | grep -E 'clock|control|sensing|vehicle'
  ```

- Ensure `/clock` is active and `use_sim_time=true` in simulator and core components.

- In adapter development mode, confirm no dummy world feeds are enabled by checking startup logs for `LAUNCH_DUMMY_VEHICLE=false`, `LAUNCH_DUMMY_PERCEPTION=false`, `LAUNCH_DUMMY_DOORS=false`.
- In planning demo mode, `LAUNCH_DUMMY_VEHICLE=true` and `LAUNCH_DUMMY_PERCEPTION=true` are expected.

## Topic integration status

`CARLA_SYNCHRONOUS_MODE` is optional: set it only when your selected bridge launch file supports the `synchronous_mode` argument.

This sample starts CARLA, the CARLA ROS bridge, and the OpenADKit stack with shared ROS time. Native CARLA bridge topics do not directly match all Autoware message types, so closed-loop CARLA driving still needs explicit adapter nodes for control/status/sensor type conversion.

ROS 2 Humble `ros2 launch` does not accept a global `--ros-args` remap block for launched nodes. The included remap files are reference templates for adapter or launch integration work, not arguments passed directly to the bridge command.

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
  - `USE_SIM_TIME=true` is enabled by default.
  - `SCENARIO_SIMULATION=false` is the default for the published OpenADKit simulator image because it does not include `autoware_dummy_infrastructure`.

If your CARLA topic role names differ, update the adapter configuration and reference remap templates accordingly.

## Reference Remap Templates

- Camera+lidar mode: default remap file
  - `carla_bridge_remap.camera_lidar.args`
- LiDAR-only mode: reference remap file
  - `carla_bridge_remap.lidar_only.args`

## Stop

```bash
docker compose --env-file carla-simulation.env --env-file carla-simulation.planning-demo.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml -f docker-compose.planning-demo.override.yaml down
```
