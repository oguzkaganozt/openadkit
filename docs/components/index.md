# Components

Open AD Kit is a component-based project designed to run on a variety of platforms with containerized services. Each **Autoware function** remains independently deployable, while the published images group closely related functions together to keep the runtime layout simpler.

## Architecture Overview

Autoware uses a **Core / Universe** architecture. **Core** contains rigorously reviewed base functionality required for safe autonomous driving. **Universe** contains community extensions and research features that build on the Core foundation. Open AD Kit packages Core components into focused container images that can be composed into complete AD systems.

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

    classDef rosBase fill:#334155,stroke:#64748b,color:#fff
    classDef commonBase fill:#1e3a5f,stroke:#3b82f6,color:#fff
    classDef componentImage fill:#14532d,stroke:#22c55e,color:#fff
```

</div>

### Build Groups

| Group | Description | Targets |
|-------|-------------|---------|
| `common` | Common base and development images | base, devel, base-cuda, devel-cuda |
| `component` | Component images | sensing-perception, sensing-perception-cuda, localization-mapping, planning-control, vehicle-system, api, visualizer, simulator |

## Interface Layers

Autoware defines three formal interface categories that govern how components communicate:

<div class="oak-component-grid">

<div class="oak-component-item">
<strong>AD API</strong>
<span>External interface for fleet management and HMI. Uses HTTP/MQTT and ROS topics for vehicle state queries and commands.</span>
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
        A1[HTTP / MQTT]
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

## End-to-End Roadmap

Autoware is evolving toward end-to-end autonomous driving through a phased roadmap. While Open AD Kit currently packages the modular v1 architecture, the project is tracking these advancements:

<div class="oak-mermaid-dark" markdown="1">

```mermaid
flowchart LR
    P1["Phase 1<br/>Learned Planning"]:::roadmapPhase --> P2["Phase 2<br/>Learned Perception"]:::roadmapPhase
    P2 --> P3["Phase 3<br/>Monolithic Network"]:::roadmapPhase
    P3 --> P4["Phase 4<br/>Learned Hybrid"]:::roadmapPhase

    classDef roadmapPhase fill:#1e3a5f,stroke:#3b82f6,color:#fff
```

</div>

<ol class="oak-steps" markdown="1">

1. **Phase 1 — Learned Planning** — Introduction of learned trajectory planning modules alongside classical planners.
2. **Phase 2 — Learned Perception** — Integration of learned perception pipelines (detection, tracking, prediction) with traditional safety-critical modules.
3. **Phase 3 — Monolithic Network** — A unified learned driving network handling perception through control.
4. **Phase 4 — Learned Hybrid** — A monolithic learned network backed by dedicated safety perception modules for guaranteed collision avoidance.

</ol>

For the full roadmap, see the [Autoware Architecture v2 Roadmap](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture-v2/roadmap/).

## Related

- [Deployments](../deployments/index.md) — How to compose components into running systems
- [Getting Started](../getting-started/index.md) — Quick start guide
- [Supported Platforms](../platforms/index.md) — Where to deploy

