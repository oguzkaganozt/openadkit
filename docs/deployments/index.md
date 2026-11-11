# Deployments

A deployment is a ready-to-run Autoware stack for one task. New users should
start with Planning Simulation.

| Deployment | Purpose | GPU | Architectures | CI evidence |
|------------|---------|-----|---------------|-------------|
| [Planning Simulation](planning-simulation/index.md) | Plan and follow a route on a sample map with the built-in simulator; `--gpu` plans with the Diffusion Planner | Optional | amd64, arm64 | Yes, in CPU mode |
| [Scenario Simulation](scenario-simulation/index.md) | Run predefined traffic scenarios in Scenario Simulator | No | amd64, arm64 | Yes |
| [Logging Simulation](logging-simulation/index.md) | Replay recorded sensor data through sensing, perception and localization | Optional | amd64, arm64 | Exempt |
| [CARLA Simulation](carla-simulation/index.md) | Drive in closed loop with the CARLA simulator | Required | amd64 | Exempt |
| [Safety Island Simulation](safety-island-simulation/index.md) | Planning Simulation driven by the [Autoware Safety Island](https://autowarefoundation.github.io/autoware-safety-island/) controller | No | amd64 | Yes |

All run on Humble and Jazzy except CARLA Simulation, which is Humble-only, and
the GPU modes are amd64-only. **CI evidence** says whether a release runs the
deployment end to end before it ships; an exempt deployment ships without that
check, and evidence runs on amd64 only. See the
[Evidence Policy](../releases/evidence.md).

Scenario and CARLA Simulation can also run as
[split-host](split-host.md) nodes, with Autoware on one host and the simulator
on another over Zenoh (experimental).

## Running a Deployment

Complete the [Quickstart](../getting-started/index.md) setup first.

```bash
openadkit list
openadkit run planning-simulation
openadkit status
openadkit logs --follow
openadkit stop
```

- Add `--ros-distro jazzy` to `validate`, `fetch`, `run` or `build` to select
  Jazzy; Humble is the default.
- Add `--gpu` for the optional GPU mode of Planning Simulation (the Diffusion
  Planner) or Logging Simulation (CenterPoint). CARLA needs a GPU, so its GPU
  mode turns on by itself.
- Put host settings in `~/.config/openadkit/<name>.env`; see
  [Configuration](../getting-started/cli.md#configuration).

[CLI & Maintenance](../getting-started/cli.md) covers the other commands.

## Your Own Kit

Start a kit with `openadkit new` ([Create a Kit](create-a-kit.md)). It extends
a deployment without copying it and keeps only your differences. The
[Integrator Guide](integrator-guide.md) is the reference for every extension
point.
