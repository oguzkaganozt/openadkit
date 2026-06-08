# Autoware Open AD Kit Planning Simulation

This sample deployment demonstrates the Open AD Kit planning simulation workflow.

## Documentation

For **complete operational instructions** including map download, startup, visualizer access, and troubleshooting, see the canonical documentation:

**[Open AD Kit Docs — Planning Simulation](https://autowarefoundation.github.io/openadkit/deployments/samples/planning-simulation/)**

## Quick Start

```bash
# From this directory
docker compose --env-file planning-simulation.env up -d
```

Open the visualizer at `http://localhost:6080/vnc.html` (password: `openadkit`).

## Stop

```bash
docker compose --env-file planning-simulation.env down
```
