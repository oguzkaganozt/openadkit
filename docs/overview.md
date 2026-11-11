# Overview

<p class="oak-hero-lead">
  What Open AD Kit is, why it exists, and how it relates to Autoware.
</p>

## What is Open AD Kit

Open AD Kit packages the [Autoware](https://github.com/autowarefoundation/autoware) autonomous driving stack as focused, independently deployable container images. Instead of one monolithic image, it splits the stack along the AD pipeline (sensing and perception, localization and mapping, planning, control, vehicle and system, API, simulator and visualizer), so a deployment runs only what its task needs.

Autoware provides the autonomy stack; Open AD Kit makes it deployable. It packages upstream software into composable images, defines deployments, integrates target platforms, and maintains the build, test and release tooling that keeps a deployment the same from one host to the next. It ships simulation deployments today; a supported path to a real vehicle interface is on the [roadmap](roadmap.md).

It also integrates [Autoware Safety Island](https://autowarefoundation.github.io/autoware-safety-island/), which runs on real-time operating systems and automotive hardware rather than in a container. Open AD Kit is the first [SOAFEE](https://www.soafee.io/) blueprint for the software-defined vehicle; [Supported Platforms](platforms/index.md) covers the derived blueprints and the support tiers.

## Why Open AD Kit

<div class="oak-card-grid oak-card-grid--four" markdown="1">

<div class="oak-card" markdown="1">

:material-view-module-outline:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Modular Components</p>
<p>Independent images for each stage of the AD pipeline. Deploy only what you need.</p>
</div>

<div class="oak-card" markdown="1">

:material-shield-half-full:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Mixed Criticality</p>
<p>Keep safety-critical control on the Safety Island's real-time hardware, beside the containerized stack.</p>
</div>

<div class="oak-card" markdown="1">

:material-cloud-sync-outline:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Cloud Native</p>
<p>Scale from simulation to the edge with containerized deployments, reproducible image builds, and platform integrations.</p>
</div>

<div class="oak-card" markdown="1">

:material-infinity:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Connected and Continuous</p>
<p>CI/CD with GitHub Actions, optimized build caching, and containerized testing.</p>
</div>

</div>

## How It Works

Open AD Kit runs Autoware as a pipeline of containers. Each container handles one stage of autonomous driving, and the stages talk over ROS 2 DDS on the host network.

1. [**Sensing**](components/index.md#sensing-perception) captures and preprocesses raw sensor data (LiDAR, camera, IMU).
2. [**Perception**](components/index.md#sensing-perception) detects and tracks objects, traffic lights, and drivable space.
3. [**Mapping**](components/index.md#localization-mapping) serves high-definition map data that the rest of the stack consumes.
4. [**Localization**](components/index.md#localization-mapping) determines the vehicle's exact position on the map.
5. [**Planning**](components/index.md#planning) computes a safe, feasible trajectory to the goal.
6. [**Control**](components/index.md#control) converts that trajectory into throttle, brake, and steering commands.
7. [**Vehicle and System**](components/index.md#vehicle-and-system) bridges those commands to the vehicle or simulator and monitors the stack.

A [deployment](deployments/index.md) runs the subset of these stages a task needs. Autoware Safety Island joins the same pipeline over DDS, adding a safety-critical actuation path alongside the containerized services.

## Key Terms

| Term | Meaning |
|------|---------|
| **Component image** | A published container image holding one or more Autoware functions, for example `planning`. |
| **Latest alias** | An image tag such as `planning-humble` that follows the newest stable release. Release tags (`-vX.Y.Z`) and digests never move. |
| **Digest pin** | An image reference by content hash (`@sha256:…`) instead of a tag, so the same image bits are always used. |
| **Deployment** | A named, ready-to-run stack for one task, such as Planning Simulation: a deployment manifest, settings and Compose files. |
| **Deployment manifest** | `deployment.json`: what the CLI needs to run a deployment. Compose files, requirements, data downloads, one-shot services and the verify step. |
| **Settings** | `KEY=value` variables a deployment runs with, such as `MAP_PATH`: `settings.env`, then `settings.gpu.env` with `--gpu`, then the host settings file. `run` and `restart` apply them. |
| **Node** | One host's part of a split-host deployment, with its own services, Compose project, ROS domain and Zenoh endpoint. |
| **Kit** | A kit manifest and its deployments: the reference kit in this repository, or your differences on top of a pinned release. |
| **Kit manifest** | `openadkit.json`: what the kit extends, its deployments (each named by its key) and the images it pins. |
| **`extends` / `base`** | The Open AD Kit release a kit pins, and the deployment of that release a kit deployment builds on. |
| **Config override** | Parameter and file differences under `config/autoware/`, merged over a package's configuration on every start; not a copy of the full file. `restart` applies them. |
| **Overlay workspace** | Your ROS packages in `overlay_ws/`, built in the release's devel image and sourced on top of Autoware. |
| **Evidence cell** | One runtime test of a deployment on one ROS distro and topology, such as `planning-simulation-humble-linux-amd64`. |
| **Evidence** | The evidence cells run against one build. A release needs a run in which every cell passed. |
| **CI exemption** | A reasoned manifest entry for a deployment without a hosted evidence cell. It is not a passing test. |
| **BOM** | A release's bill of materials: the pinned Autoware release, component images and external images. |
| **Mixed criticality** | Running safety-critical and non-critical workloads on separately qualified execution environments. Here, the Safety Island's real-time hardware beside the containerized stack; the containers on one host share its network and are not isolated by criticality. |
