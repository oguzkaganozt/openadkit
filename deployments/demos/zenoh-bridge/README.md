# Zenoh Bridge Demo

This project demonstrates how to bridge Autoware data from Edge to Cloud using Zenoh.

## Documentation

For **complete architecture documentation**, setup instructions, troubleshooting, and multi-machine deployment details, see the canonical documentation:

**[Open AD Kit Docs — Zenoh Bridge Demo](https://autowarefoundation.github.io/openadkit/deployments/demos/zenoh-bridge/)**

## Demo Video

[![[openadkit x zenoh-bridge] remote control (cloud/edge) demo](https://img.youtube.com/vi/6yhhxlVQTKI/0.jpg)](https://www.youtube.com/watch?v=6yhhxlVQTKI)

## Quick Start

### Split Topology (Recommended)

```bash
./edge.sh up -d
./cloud.sh up -d
```

Access the visualizer at `http://localhost:6081` (password: `openadkit`).

### Monolithic

```bash
docker compose up -d
```

## Teleoperation Controls

Launch the teleop interface with `./run_teleop.sh`.

| Key | Function |
|-----|----------|
| **W/S** | Throttle / Brake |
| **A/D** | Turn Left / Right |
| **Z** | Toggle Auto/Local Control |
| **Space** | Emergency Stop / Resume |
| **Q** | Quit |

## CLI Reference

| Command | Description |
|---------|-------------|
| `up -d` | Start services in background |
| `down` | Stop and remove services |
| `dry-run` | Preview config without starting |

## Shutdown

```bash
./cloud.sh down
./edge.sh down
```
