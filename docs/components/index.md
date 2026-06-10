# Components

Open AD Kit is a component-based project designed to run on a variety of platforms with containerized services. Each **Autoware function** remains independently deployable, while the published images group closely related functions together to keep the runtime layout simpler.

## Architecture Overview

Autoware uses a **Core / Universe** architecture. **Core** contains rigorously reviewed base functionality required for safe autonomous driving. **Universe** contains community extensions and research features that build on the Core foundation. Open AD Kit packages Universe components into focused container images that can be composed into complete AD systems.

## Build Pipeline

<div class="oak-mermaid-dark oak-pipeline-diagram" markdown="1">

```mermaid
flowchart TB
    ROS["ros:humble-ros-base-jammy<br/>ros:jazzy-ros-base-noble"]:::rosBase --> CB["common-base"]:::commonBase
    CB --> CD["common-devel"]:::commonBase

    CD --> SP["sensing-perception"]:::componentImage
    CD --> LM["localization-mapping"]:::componentImage
    CD --> PC["planning-control"]:::componentImage
    CD --> VS["vehicle-system"]:::componentImage
    CD --> API["api"]:::componentImage
    CD --> VIZ["visualizer"]:::componentImage
    CD --> SIM["simulator"]:::componentImage
    SIM --> CARLA["carla-interface"]:::componentImage

    classDef rosBase fill:#334155,stroke:#64748b,color:#fff
    classDef commonBase fill:#1e3a5f,stroke:#3b82f6,color:#fff
    classDef componentImage fill:#14532d,stroke:#22c55e,color:#fff
```

</div>

### Build Groups

| Group | Description | Targets |
|-------|-------------|---------|
| `common` | Common base and development images | base, devel, base-cuda, devel-cuda |
| `component` | Component images | sensing-perception, sensing-perception-cuda, localization-mapping, planning-control, vehicle-system, api, visualizer, simulator, carla-interface |

## Interface Layers

Autoware defines three formal interface categories that govern how components communicate:

<div class="oak-component-grid">

<div class="oak-component-item">
<strong>AD API</strong>
<span>External interface for fleet management and HMI. Exposed as ROS 2 services and topics for vehicle state queries and commands; external gateways (e.g. HTTP/MQTT) can be layered on top.</span>
</div>

<div class="oak-component-item">
<strong>Component Interface</strong>
<span>Internal inter-module communication via ROS 2 topics and services. Standardized message types ensure compatibility across components.</span>
</div>

<div class="oak-component-item">
<strong>Local Interface</strong>
<span>Intra-component communication within a single image. Implementation details that do not cross component boundaries.</span>
</div>

</div>

```mermaid
graph LR
    subgraph AD_API["AD API (External)"]
        A1[ROS 2 Services / Topics]
    end

    subgraph Component_Interface["Component Interface"]
        C1[ROS 2 Topics]
        C2[ROS 2 Services]
    end

    subgraph Local_Interface["Local Interface"]
        L1[Intra-component Communication]
    end

    AD_API --> Component_Interface
    Component_Interface --> Local_Interface
```

## Autoware Components

Each Autoware function is packaged into a focused container image. Select a component from the sidebar or explore the pages below.

<div class="oak-component-grid">

<div class="oak-component-item">
<strong><a href="sensing/">Sensing</a></strong>
<span>LiDAR, cameras, radar, ultrasonics, and GNSS-INS preprocessing.</span>
</div>

<div class="oak-component-item">
<strong><a href="perception/">Perception</a></strong>
<span>Object detection, tracking, and multi-sensor fusion.</span>
</div>

<div class="oak-component-item">
<strong><a href="mapping/">Mapping</a></strong>
<span>Occupancy grid and point cloud map construction.</span>
</div>

<div class="oak-component-item">
<strong><a href="localization/">Localization</a></strong>
<span>GNSS, IMU, visual odometry, and LiDAR map matching.</span>
</div>

<div class="oak-component-item">
<strong><a href="planning/">Planning</a></strong>
<span>Route, behavior, motion, and goal planning.</span>
</div>

<div class="oak-component-item">
<strong><a href="control/">Control</a></strong>
<span>PID and MPC trajectory tracking with vehicle actuation.</span>
</div>

<div class="oak-component-item">
<strong><a href="vehicle-system/">Vehicle and System</a></strong>
<span>Vehicle interface and system-level orchestration services.</span>
</div>

<div class="oak-component-item">
<strong><a href="api/">API</a></strong>
<span>AD API for external fleet management and HMI integration.</span>
</div>

<div class="oak-component-item">
<strong><a href="simulator/">Simulator</a></strong>
<span>Closed-loop simulation for validation and local development.</span>
</div>

<div class="oak-component-item">
<strong><a href="visualizer/">Visualizer</a></strong>
<span>Browser-accessible RViz via noVNC for remote monitoring.</span>
</div>

<div class="oak-component-item">
<strong><a href="carla-interface/">CARLA Interface</a></strong>
<span>Bridge for closed-loop simulation with the CARLA simulator.</span>
</div>

</div>

## Open AD Kit Roadmap

Open AD Kit tracks Autoware's architecture evolution upstream, but its own roadmap is focused on **containerization, platform support, and CI/CD** rather than on the autonomy algorithms themselves. The goal is to package whatever Autoware ships into clean, composable, production-ready images.

!!! note "Placeholder"
    A detailed Open AD Kit roadmap is being prepared. Current focus areas include:

    - **Containerization** — Splitting the monolithic stack into focused component images and retiring `autoware:universe` fallbacks (see deployment *Known Limitations*).
    - **Platform support** — Expanding verified coverage across edge and cloud targets (see [Platforms](../platforms/index.md)).
    - **CI/CD** — Multi-architecture builds, image scanning, and a reproducible release flow (see [Release Flow](../getting-started/release-flow.md)).

For Autoware's upstream autonomy direction, see the [Autoware architecture documentation](https://autowarefoundation.github.io/autoware-documentation/main/design/).

## Related

- [Deployments](../deployment/index.md) — How to compose components into running systems
- [Getting Started](../getting-started/index.md) — Quick start guide
- [Supported Platforms](../platforms/index.md) — Where to deploy
