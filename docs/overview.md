# Overview

<p class="oak-hero-lead">
A modular, container-based distribution of <a href="https://github.com/autowarefoundation/autoware">Autoware</a> for building autonomous driving systems — from development laptops to vehicle edge deployment.
</p>

## What is Open AD Kit

Open AD Kit packages the [Autoware](https://github.com/autowarefoundation/autoware) autonomous driving stack as a set of focused, independently deployable container images. Rather than shipping one monolithic image, it splits the stack along the AD pipeline — sensing, perception, localization, mapping, planning, control, and supporting services — so you can run only what a given workload needs.

Its mission is **containerization**: taking what Autoware produces upstream and delivering it as clean, composable, production-ready images that run consistently everywhere — from a development laptop, to cloud simulation, to a vehicle's edge compute. The autonomy algorithms come from Autoware; Open AD Kit owns how they are built, packaged, tested, and deployed.

!!! abstract "SOAFEE Blueprint"
    The first [SOAFEE](https://soafee.io/) blueprint for the software-defined vehicle, co-developed with the [eSync Alliance](https://www.esyncalliance.com/). Learn more on the [Platforms](platforms/index.md) page.

## Why Open AD Kit

<div class="oak-card-grid" markdown="1">

<div class="oak-card" markdown="1">

:material-view-module-outline:{ .oak-card-icon }

<h3>Modular Components</h3>
<p>Independent images for each stage of the AD pipeline. Deploy only what you need.</p>
</div>

<div class="oak-card" markdown="1">

:material-shield-half-full:{ .oak-card-icon }

<h3>Mixed Criticality</h3>
<p>Separate safety-critical and non-critical workloads across certified and standard hardware.</p>
</div>

<div class="oak-card" markdown="1">

:material-cloud-sync-outline:{ .oak-card-icon }

<h3>Cloud Native</h3>
<p>Scale from laptop to edge with Docker Compose, Docker Bake, and platform integrations.</p>
</div>

<div class="oak-card" markdown="1">

:material-infinity:{ .oak-card-icon }

<h3>Connected and Continuous</h3>
<p>CI/CD with GitHub Actions, optimized build caching, and containerized testing.</p>
</div>

</div>

## Related

- [Getting Started](getting-started/index.md) — Set up your environment
- [Deployment](deployment/index.md) — Run your first sample
- [Platforms](platforms/index.md) — Choose a deployment target
