# Open AD Kit Deployments

The deployments the CLI and the release bundle ship. The
[documentation site](https://autowarefoundation.github.io/openadkit/deployments/)
is the canonical reference for running, configuring and troubleshooting them.

| Directory | Deployment |
| --- | --- |
| [`planning-simulation/`](./planning-simulation) | Plan and follow a route on a sample map with the built-in simulator; `--gpu` plans with the Diffusion Planner |
| [`scenario-simulation/`](./scenario-simulation) | Run predefined traffic scenarios in Scenario Simulator |
| [`logging-simulation/`](./logging-simulation) | Replay recorded sensor data through sensing, perception and localization |
| [`carla-simulation/`](./carla-simulation) | Drive in closed loop with the CARLA simulator (Humble, amd64, NVIDIA GPU) |
| [`safety-island-simulation/`](./safety-island-simulation) | Planning Simulation driven by the Autoware Safety Island controller (amd64) |
| `shared/` | What the deployments share: `services/*.yaml`, `runtime.env`, `cyclonedds.xml`, `compose.zenoh.yaml`, launch files and checks |

Each deployment directory holds its deployment manifest (`deployment.json`),
its settings (`settings.env`, and `settings.gpu.env` for a GPU mode) and its
Compose files. Scenario and CARLA Simulation also declare
[split-host](https://autowarefoundation.github.io/openadkit/deployments/split-host/)
nodes (`--node` over Zenoh, experimental).
