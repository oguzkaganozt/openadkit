# Autoware Open AD Kit CARLA E2E Simulation

This sample runs a closed-loop CARLA 0.9.16 end-to-end simulation with modular OpenADKit containers and Autoware's `autoware_carla_interface`.

The default flow uses the official CARLA Ubuntu 22 container image and does not use the CARLA ROS bridge, dummy vehicle, dummy perception, a monolithic Autoware container, or a host-installed CARLA runtime.

## Runtime

- CARLA: `carlasim/carla:0.9.16`
- CARLA interface image: `local/openadkit-carla-interface:0.9.16`
- Autoware modules: standard OpenADKit split images
- CARLA map: `Town01`
- Autoware map assets: downloaded to `$HOME/autoware_data/maps/Town01`
- RViz/noVNC: `ghcr.io/autowarefoundation/openadkit:visualizer`

The CARLA container runs on the host X display with NVIDIA GPU access. The helper mounts `/tmp/.X11-unix` and the host NVIDIA Vulkan ICD so CARLA renders through the NVIDIA driver instead of Mesa lavapipe.

## Requirements

- Docker with NVIDIA Container Toolkit
- Access to `carlasim/carla:0.9.16`
- A working host X display, usually `DISPLAY=:0`
- Host NVIDIA Vulkan ICD at `/usr/share/vulkan/icd.d/nvidia_icd.json`

## Start

Run from the sample directory:

```bash
cd deployments/samples/carla-simulation
./start-carla-e2e-demo.sh
```

The helper will:

- Build `local/openadkit-carla-interface:0.9.16` with `carla==0.9.16`.
- Download the official CARLA Autoware Town01 map assets if missing.
- Start `carlasim/carla:0.9.16` as `carla-e2e` on `DISPLAY=:0`.
- Preload `Town01`.
- Start modular OpenADKit map, system, CARLA interface, sensing, perception, localization, planning, vehicle, control, and API containers.
- Start the browser RViz/noVNC visualizer.
- Verify localization, CARLA LiDAR, and the CARLA ego actor.

The default behavior is no-drive. Set the route and engage manually in RViz.

## Open RViz

If running remotely, forward noVNC from the machine running the sample:

```bash
ssh -L 8080:localhost:6080 <user>@<host>
```

Open:

```text
http://localhost:8080/vnc.html
```

Password:

```text
openadkit
```

In RViz:

- Use `2D Goal Pose` to set a route.
- Wait for routing and planning to become available.
- Click `Auto` to engage autonomous driving.

## Optional Drive Check

To automatically set a short forward route, engage autonomous mode, and verify movement:

```bash
./start-carla-e2e-demo.sh --drive
```

Expected success output includes:

```text
Route set: start=(..., ...) goal=(..., ...)
Autonomous mode active
Moved ... m: start=(..., ...) current=(..., ...)
```

## Faster Relaunch

After the e2e image has already been built:

```bash
./start-carla-e2e-demo.sh --skip-build
```

For start-only behavior with an explicit no-drive flag:

```bash
./start-carla-e2e-demo.sh --skip-build --no-drive
```

## Command Path

Closed-loop control uses this path:

```text
/control/command/control_cmd
  -> autoware_raw_vehicle_cmd_converter
  -> /control/command/actuation_cmd
  -> autoware_carla_interface
  -> CARLA ego vehicle
```

## Stop

```bash
docker rm -f autoware-e2e-carla autoware-e2e-visualizer carla-e2e
```
