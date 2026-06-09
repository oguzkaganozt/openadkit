# Custom Deployment

This guide shows how to compose your own Open AD Kit deployment from OAK component images using Docker Compose.

## Prerequisites

- Docker Engine
- Optional: NVIDIA Container Toolkit (for GPU-accelerated components)
- Open AD Kit repository cloned

## Component Selection

Choose which OAK images to use based on your use case:

### Minimal Stack

The simplest useful deployment runs just planning and visualization:

| Component | Image | Purpose |
|-----------|-------|---------|
| `visualizer` | `ghcr.io/autowarefoundation/openadkit/visualizer` | Browser-accessible RViz |
| `planning-control` | `ghcr.io/autowarefoundation/openadkit/planning-control` | Planning and control logic |

### Full Simulation Stack

Add a simulator to test planning without real sensors:

| Component | Image | Purpose |
|-----------|-------|---------|
| `visualizer` | `ghcr.io/autowarefoundation/openadkit/visualizer` | Browser-accessible RViz |
| `planning-control` | `ghcr.io/autowarefoundation/openadkit/planning-control` | Planning and control logic |
| `simulator` | `ghcr.io/autowarefoundation/openadkit/simulator` | Virtual vehicle and environment |

### Full Perception Stack

Run the complete Autoware pipeline with sensing and perception:

| Component | Image | Purpose |
|-----------|-------|---------|
| `visualizer` | `ghcr.io/autowarefoundation/openadkit/visualizer` | Browser-accessible RViz |
| `sensing-perception` | `ghcr.io/autowarefoundation/openadkit/sensing-perception` | Sensor preprocessing and perception |
| `localization-mapping` | `ghcr.io/autowarefoundation/openadkit/localization-mapping` | Localization and map serving |
| `planning-control` | `ghcr.io/autowarefoundation/openadkit/planning-control` | Planning and control logic |
| `vehicle-system` | `ghcr.io/autowarefoundation/openadkit/vehicle-system` | Vehicle interface and system services |
| `api` | `ghcr.io/autowarefoundation/openadkit/api` | External API services |

!!! tip "GPU-Accelerated Perception"
    Use the `sensing-perception-cuda` image instead of `sensing-perception` for GPU-accelerated inference. This is **amd64-only** and requires NVIDIA Container Toolkit.

## Example Compose File

Here is a minimal `docker-compose.yaml` for a Planning Simulation-like stack:

```yaml
services:
  planning-control:
    image: ghcr.io/autowarefoundation/openadkit/planning-control
    volumes:
      - ~/autoware_map:/autoware_map:ro
    environment:
      - ROS_DOMAIN_ID=0
    command: >
      ros2 launch tier4_planning_component tier4_planning_component.launch.xml

  visualizer:
    image: ghcr.io/autowarefoundation/openadkit/visualizer
    ports:
      - "6080:6080"
    environment:
      - ROS_DOMAIN_ID=0
    command: >
      ros2 launch tier4_visualizer_component tier4_visualizer_component.launch.xml
```

## Environment Configuration

Create a `.env` file alongside your `docker-compose.yaml`:

```bash
# Required
ROS_DOMAIN_ID=0

# Optional: NVIDIA runtime (for GPU-accelerated images)
# NVIDIA_VISIBLE_DEVICES=all
# NVIDIA_DRIVER_CAPABILITIES=all
```

## Starting the Deployment

```bash
# Start the stack
docker compose up -d

# Verify all containers are running
docker compose ps

# View logs
docker compose logs -f

# Stop the stack
docker compose down
```

## Next Steps

- For a complete, ready-to-run example, see the [Planning Simulation](samples/planning-simulation/index.md)
- For GPU-accelerated deployments, see the [Logging Simulation](samples/logging-simulation/index.md)
- For distributed deployments, see the [Zenoh Bridge Demo](demos/zenoh-bridge/index.md)

!!! note "Future Work"
    A unified master deployment configuration is planned to serve as both documentation and a golden-path setup for all OAK components.

## Related

- [Component Overview](../components/index.md) — Understand the full OAK architecture
- [Container Image Tags](../getting-started/image-tags.md) — Choose the right tag
- [Getting Started](../getting-started/index.md) — Environment setup
