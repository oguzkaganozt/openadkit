# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An Open AD Kit integrator kit: Autoware's Autoware services running against
`verve_sim`, where CARLA and Project Chrono own the world and the ego. It
extends `carla-simulation` but does **not** include its CARLA services — the
base's `carla`, `carla-map-loader` and `carla-interface` would spawn a second
ego and tick the world themselves.

Read `../../docs/deployments/custom-deployment.md` and the base
`deployments/carla-simulation/` before changing the Compose files.

## Commands

Run from this directory; the CLI resolves the kit from the current directory.

```bash
../../openadkit validate verve-m2          # manifest, data and Compose model
../../openadkit fetch verve-m2             # Town01 lanelet + NDT point cloud
../../openadkit run verve-m2               # with RViz at :6080 (openadkit)
../../openadkit run verve-m2 --no-visualizer
../../openadkit stop verve-m2
bash overlay_ws/build.sh humble            # after editing overlay_ws/src
```

The paired stack lives in the `verve_sim` checkout: `docker compose up -d ros`
starts the world, the vehicle and the ROS bridge. Autoware and verve_sim must
both run for anything to move.

## Layout

| Path | Job |
|---|---|
| `openadkit.json` | Kit manifest; pins the fork's component images by digest |
| `deployment.json` | Base deployment and the Town01 map download |
| `config.env` | Everything that differs from the base's values |
| `docker-compose.yaml` | Includes the shared services directly, defines the stub |
| `config/autoware/` | Parameter overrides merged over Autoware's files |
| `overlay_ws/src/` | The M2 packages, built into `overlay_ws/install` |

`overlay_ws/src` holds copies of `verve_m2_vehicle/autoware` packages. The
only intended divergence is `verve_m2_layout4cam1lidar_sensor_kit_launch/launch/imu.launch.xml`,
which drops the tamagawa driver (no device, not in the images). Keep other
edits out, or they will be lost the next time the packages are copied.

## Things that look wrong but are deliberate

- **The shared services are listed individually** instead of
  `include: ${OPENADKIT_BASE_DEPLOYMENT}/docker-compose.yaml`. The base's
  entry file wires every service to `carla-interface`; Compose replaces
  `depends_on` wholesale on merge, so those edges cannot be removed.
- **`carla-map-loader` is a busybox `sleep infinity` stub.** The base lists
  it in `resetServices`, so Compose must resolve it; it is only ever
  `compose rm`'d and never starts. Without it, `openadkit run` fails with
  "manifest references unknown Compose service(s)".
- **`SYSTEM_RUN_MODE=online`, `IS_SIMULATION_MODE=false`.** The mode only
  decides the pose initializer's stop check
  (`autoware_launch component_localization.launch.xml`). It passes because
  verve_sim's plant now has a park brake that holds the M2 genuinely still;
  without one the tire jitter trips the check.
- **`LAUNCH_VEHICLE_INTERFACE=false`.** verve_sim's `ros` service is the
  vehicle interface; a second one fights it for the command topics.
- The `overlay contract: ... replaces the base image` warnings are expected:
  the kit runs the fork's images, not upstream's.

## What works

Localization initializes in `online` mode, a route sets, autonomous mode
engages and the M2 drives the route to its goal. The route has to stay on
lanelet 1157's straight (Town01's flat east-west road at y ≈ −59): a goal
much past x ≈ 340 comes back "The planned route is empty", because the
lanelet ends there, not because of a fault.

Localization is started by hand, as on any Autoware stack:

```bash
# in autoware-localization, with ROS_DOMAIN_ID=1 and CycloneDDS on lo:
ros2 service call /api/localization/initialize ...  # or an initial pose in RViz
```

The pose to give it is the one verve_sim publishes on
`/sensing/gnss/pose_with_covariance`; `y` there is already in Autoware's map
frame (CARLA's y negated).

## RViz

`http://localhost:6080/vnc.html`, password `REMOTE_PASSWORD` (`openadkit`).
**Use `http://`, not `https://`**: the page picks `wss://` when it is loaded
over https, and websockify's self-signed certificate is what the browser then
refuses. Over http it uses plain `ws://`, which the same websockify serves.

## Steering

`max_steer_angle` in the M2's `vehicle_info.param.yaml` (0.6435 rad, 36.87°)
is the measured limit of the real vehicle, but the Chrono plant stops at
29° (30.8° with tire compliance). Autoware asks for up to 36.87° and the plant
saturates, so the lateral controller sees a persistent error at full lock.
Not a blocker -- the route here is straight -- but it will matter on a turn.
