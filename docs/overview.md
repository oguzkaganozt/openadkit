# Overview

<p class="oak-hero-lead">
  What Open AD Kit is, why it exists, and how it relates to Autoware.
</p>

## What is Open AD Kit

Open AD Kit packages the [Autoware](https://github.com/autowarefoundation/autoware) autonomous driving stack as focused, independently deployable container images. Instead of one monolithic image, it splits the stack along the AD pipeline (sensing and perception, localization and mapping, planning, control, vehicle and system, API, simulator and visualizer), so a deployment runs only what its task needs.

Autoware provides the autonomy stack; Open AD Kit makes it deployable. It packages upstream software into composable images, defines deployments, integrates target platforms, and maintains the build, test and release tooling that keeps a deployment the same from one host to the next. It ships simulation deployments today; a supported path to a real vehicle interface is planned.

It also integrates [Autoware Safety Island](https://autowarefoundation.github.io/autoware-safety-island/), which runs on real-time operating systems and automotive hardware rather than in a container. Open AD Kit is the first [SOAFEE](https://www.soafee.io/) blueprint for the software-defined vehicle; [Supported Platforms](platforms/index.md) covers the derived blueprints and the support tiers.

A [kit](kits/create-a-kit.md) is also the form in which an Autoware Reference Design can publish its software stack; see [Reference Designs](kits/reference-designs.md).

Open AD Kit is not a custom OTA service, a Kubernetes stack or a fork of
upstream workloads, and it makes no ASIL or NCAP certification claim. Safety
Island owns its safety boundary; Open AD Kit integrates it.

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
<p>Every release promotes a CI build that passed its runtime evidence, with pinned image digests and build provenance.</p>
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
7. [**Vehicle & System**](components/index.md#vehicle-and-system) bridges those commands to the vehicle or simulator and monitors the stack.

A [deployment](deployments/index.md) runs the subset of these stages a task needs. Autoware Safety Island joins the same pipeline over DDS, adding a safety-critical actuation path alongside the containerized services.

The [Glossary](glossary.md) defines the terms these docs use.
