# Open AD Kit Components

This directory contains scripts and configurations to build Open AD Kit container images.

## Documentation

For **complete component documentation**, architecture overview, and visualizer settings, see the [Open AD Kit Components Documentation](https://autowarefoundation.github.io/openadkit/components/).

## Build Pipeline

```mermaid
flowchart TB
    ROS["ros:humble-ros-base-jammy<br/>ros:jazzy-ros-base-noble"] --> CB["common-base"]
    CB --> CD["common-devel"]

    CD --> SP["sensing-perception"]
    CD --> LM["localization-mapping"]
    CD --> PC["planning-control"]
    CD --> VS["vehicle-system"]
    CD --> API["api"]
    CD --> VIZ["visualizer"]
    CD --> SIM["simulator"]

    classDef ros fill:#334155,stroke:#64748b,color:#fff
    classDef common fill:#1e3a5f,stroke:#3b82f6,color:#fff
    classDef component fill:#14532d,stroke:#22c55e,color:#fff

    class ROS ros
    class CB,CD common
    class SP,LM,PC,VS,API,VIZ,SIM component
```

### Build Groups

| Group | Description | Targets |
|-------|-------------|---------|
| `common` | Common images | base, devel, base-cuda, devel-cuda |
| `component` | Component images | sensing-perception, sensing-perception-cuda, localization-mapping, planning-control, vehicle-system, api, visualizer, simulator |
