<div align="center">

# Open AD Kit

**The deployment layer for the Autoware ecosystem.**

[Autoware](https://github.com/autowarefoundation/autoware), packaged into focused container images and ready-to-run deployments.<br>
One CLI runs them the same way on every host.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://autowarefoundation.github.io/openadkit/)
[![Autoware Discord](https://img.shields.io/discord/953808765935816715?logo=discord&logoColor=white&style=flat&label=Autoware)](https://discord.gg/Q94UsPvReQ)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/images/readme-hero-dark.svg">
  <img src="docs/assets/images/readme-hero-light.svg" width="880" alt="One command, openadkit run planning-simulation, starts Autoware as separate containers that talk over ROS 2: localization-mapping, planning, control, vehicle-system, simulator, visualizer and api.">
</picture>

</div>

Autoware provides the autonomy stack; Open AD Kit makes it deployable. Each stage of the driving pipeline is its own image, so a deployment runs only what its task needs, and [Autoware Safety Island](https://autowarefoundation.github.io/autoware-safety-island/) joins the same stack. The aim is one reproducible path from simulation to in-vehicle systems.

## Quickstart

Three commands on Ubuntu 22.04 or 24.04. No GPU needed.

> [!NOTE]
> **v2.0.0 is not published yet.** Until it is, [build the images from a source checkout](https://autowarefoundation.github.io/openadkit/development/build-from-source/) and run the commands below as `./openadkit` from its root, without the `install` step.

```bash
# 1. Install the CLI
curl -fsSL https://github.com/autowarefoundation/openadkit/releases/latest/download/openadkit \
  | bash -s -- install

# 2. Prepare the host
openadkit setup --verify

# 3. Start Autoware
openadkit run planning-simulation
```

Then open <http://localhost:6080/vnc.html>, sign in with `openadkit`, and set a goal. The vehicle plans the route and drives it.

`openadkit stop` shuts it down. Stuck, or want the details? See the full [Quickstart](https://autowarefoundation.github.io/openadkit/getting-started/).

## Deployments

| Deployment | What it runs | GPU |
|---|---|---|
| [`planning-simulation`](https://autowarefoundation.github.io/openadkit/deployments/planning-simulation/) | Plan and follow a route on a sample map | Optional |
| [`scenario-simulation`](https://autowarefoundation.github.io/openadkit/deployments/scenario-simulation/) | Predefined traffic scenarios in Scenario Simulator | No |
| [`logging-simulation`](https://autowarefoundation.github.io/openadkit/deployments/logging-simulation/) | Replay recorded sensor data, from sensing to localization | Optional |
| [`carla-simulation`](https://autowarefoundation.github.io/openadkit/deployments/carla-simulation/) | Closed-loop driving in the CARLA simulator | Required |
| [`safety-island-simulation`](https://autowarefoundation.github.io/openadkit/deployments/safety-island-simulation/) | Planning Simulation driven by the Safety Island controller | No |

`openadkit list` prints this catalog. With `--gpu`, Planning Simulation plans with the Diffusion Planner. CARLA requires Humble, amd64 and an NVIDIA GPU; Safety Island Simulation requires amd64. [Split-host Simulation](https://autowarefoundation.github.io/openadkit/deployments/split-host/) (`--node` over Zenoh) is experimental.

## Create a Kit

A kit holds only your differences from a deployment: your ROS packages, parameter overrides and extra services.

```bash
openadkit new my-kit        # on top of planning-simulation
cd my-kit
openadkit build             # your overlay workspace
openadkit run --verify      # start, wait until ready, run the end-to-end check
```

[Create a Kit](https://autowarefoundation.github.io/openadkit/kits/create-a-kit/) covers the layout and each extension point.

## Documentation

- [**Overview**](https://autowarefoundation.github.io/openadkit/overview/) — what Open AD Kit is and how it is put together
- [**CLI & Maintenance**](https://autowarefoundation.github.io/openadkit/getting-started/cli/) — every command, configuration, upgrades and cleanup
- [**Components**](https://autowarefoundation.github.io/openadkit/components/) — the container images and what each one runs
- [**Platforms**](https://autowarefoundation.github.io/openadkit/platforms/) — support tiers, AutoSD and host requirements
- [**Releases**](https://autowarefoundation.github.io/openadkit/releases/) — what a release ships, promises and proves
- [**Build from Source**](https://autowarefoundation.github.io/openadkit/development/build-from-source/) — build the images yourself

## Community

- **Working Group** — open to everyone, every Thursday at 13:00 UTC: [add it to your calendar](https://www.google.com/calendar/event?eid=YnY4dmJxZTVsM2h2cWE1cTJ2NmhtOWdwMzZfMjAyNjA5MjRUMTMwMDAwWiBhdXRvd2FyZS5vcmdfNmxvbDBobzVmdDAyMTdoOGM2MHBpMWZtMzBAZw), read the [agendas and notes](https://github.com/orgs/autowarefoundation/discussions?discussions_q=label%3Ameeting%3Aopenadkit-wg), or see the [wiki](https://github.com/autowarefoundation/autoware-projects/wiki/Open-AD-Kit-Working-Group)
- **Chat** — questions and design discussions on the [Autoware Discord](https://discord.gg/Q94UsPvReQ)
- **Contribute** — [CONTRIBUTING.md](CONTRIBUTING.md) has the development workflow and validation steps

## License

Apache License 2.0. See [LICENSE](LICENSE).
