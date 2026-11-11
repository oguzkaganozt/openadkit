# Open AD Kit

<div align="center">

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://autowarefoundation.github.io/openadkit/)
[![Autoware Discord](https://img.shields.io/discord/953808765935816715?logo=discord&logoColor=white&style=flat&label=Autoware)](https://discord.gg/Q94UsPvReQ)
[![Autoware](https://img.shields.io/badge/Linkedin-Autoware-0a66c2?logo=linkedin&logoColor=white&style=flat)](https://www.linkedin.com/company/the-autoware-foundation/)

</div>

> The deployment layer for the [Autoware](https://github.com/autowarefoundation/autoware) ecosystem: packaging its software into reproducible deployments, built for the path from simulation to in-vehicle systems.

Open AD Kit packages Autoware into focused component images and ready-to-run deployments, and integrates [Autoware Safety Island](https://autowarefoundation.github.io/autoware-safety-island/) with the deployed stack. Its CLI, deployment assets, and build and release automation run autonomous driving and ADAS systems the same way on every host. Today it ships simulation deployments; vehicle integration is [planned](https://github.com/autowarefoundation/openadkit/issues).

Open AD Kit is the first [SOAFEE](https://www.soafee.io/) blueprint for the software-defined vehicle.

## Quickstart

Run Planning Simulation on Ubuntu 22.04 or 24.04. No GPU is required.

> **v2.0.0 is not published yet.** Until it is, there is no release to install: [build the images from a source checkout](https://autowarefoundation.github.io/openadkit/development/build-from-source/) and run the commands below as `./openadkit` from its root, without the `install` step.

```bash
curl -fsSL https://github.com/autowarefoundation/openadkit/releases/latest/download/openadkit \
  | bash -s -- install
openadkit setup --verify
# Run this if setup adds you to the Docker group, or start a new login session:
newgrp docker
openadkit run planning-simulation
```

The installer verifies the release bundle and puts `openadkit` in `~/.local/bin`. `run` downloads the sample map, pulls the images, starts the services and returns once the stack is ready. It prints the visualizer address; open it and sign in with the password `openadkit`.

The [Quickstart](https://autowarefoundation.github.io/openadkit/getting-started/) walks through each step and the installation options.

## Deployments

| Deployment | Purpose | GPU |
|---|---|---|
| [`planning-simulation`](https://autowarefoundation.github.io/openadkit/deployments/planning-simulation/) | Plan and follow a route on a sample map with the built-in simulator; `--gpu` plans with the Diffusion Planner | Optional |
| [`scenario-simulation`](https://autowarefoundation.github.io/openadkit/deployments/scenario-simulation/) | Run predefined traffic scenarios in Scenario Simulator | No |
| [`logging-simulation`](https://autowarefoundation.github.io/openadkit/deployments/logging-simulation/) | Replay recorded sensor data through sensing, perception and localization | Optional |
| [`carla-simulation`](https://autowarefoundation.github.io/openadkit/deployments/carla-simulation/) | Drive in closed loop with the CARLA simulator | Required |
| [`safety-island-simulation`](https://autowarefoundation.github.io/openadkit/deployments/safety-island-simulation/) | Planning Simulation driven by the [Autoware Safety Island](https://autowarefoundation.github.io/autoware-safety-island/) controller | No |

`openadkit list` prints this catalog. CARLA requires Humble, amd64 and an NVIDIA GPU; Safety Island Simulation requires amd64. [Split-host Simulation](https://autowarefoundation.github.io/openadkit/deployments/split-host/) (`--node` over Zenoh) is experimental.

## Documentation

The [documentation site](https://autowarefoundation.github.io/openadkit/) covers:

- [Architecture and components](https://autowarefoundation.github.io/openadkit/overview/)
- [Deployments](https://autowarefoundation.github.io/openadkit/deployments/)
- [Create a kit](https://autowarefoundation.github.io/openadkit/kits/create-a-kit/)
- [Supported platforms](https://autowarefoundation.github.io/openadkit/platforms/)
- [Container images and versioning](https://autowarefoundation.github.io/openadkit/releases/container-images/)
- [Compatibility](https://autowarefoundation.github.io/openadkit/releases/compatibility/)
- [Building from source](https://autowarefoundation.github.io/openadkit/development/build-from-source/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and validation steps.

The [Open AD Kit Working Group](https://github.com/autowarefoundation/autoware-projects/wiki/Open-AD-Kit-Working-Group) is open to everyone and meets every Thursday at 13:00 UTC. [Add the meeting to Google Calendar](https://www.google.com/calendar/event?eid=YnY4dmJxZTVsM2h2cWE1cTJ2NmhtOWdwMzZfMjAyNjA5MjRUMTMwMDAwWiBhdXRvd2FyZS5vcmdfNmxvbDBobzVmdDAyMTdoOGM2MHBpMWZtMzBAZw) for joining details, and browse the [meeting archive](https://github.com/orgs/autowarefoundation/discussions?discussions_q=label%3Ameeting%3Aopenadkit-wg) for agendas and notes.

For questions and design discussions, join the [Autoware Discord](https://discord.gg/Q94UsPvReQ).

## License

Apache License 2.0 - see [LICENSE](LICENSE).
