# Open AD Kit

<p class="oak-hero-lead">
The deployment layer for the <a href="https://github.com/autowarefoundation/autoware">Autoware</a> ecosystem: packaging its software into reproducible deployments, built for the path from simulation to in-vehicle systems.
</p>

<p class="oak-hero-meta">
<span class="oak-badge oak-badge--accent">First SOAFEE blueprint</span>
<span class="oak-badge oak-badge--neutral">Cloud-native containers</span>
<span class="oak-badge oak-badge--neutral">Simulation to in-vehicle</span>
</p>

## Start Here { .oak-eyebrow }

<div class="oak-card-grid oak-card-grid--four" markdown="1">

<div class="oak-card" markdown="1">

:material-rocket-launch-outline:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Try it locally</p>
<p>Run Planning Simulation on Ubuntu in about 10 minutes. No GPU, no build from source.</p>
<a href="getting-started/" class="md-button md-button--primary">Quickstart</a>
</div>

<div class="oak-card" markdown="1">

:material-cube-outline:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Run a deployment</p>
<p>Planning, scenario, logging, CARLA and Safety Island simulation, on one host or split over Zenoh.</p>
<a href="deployments/" class="md-button">Deployments</a>
</div>

<div class="oak-card" markdown="1">

:material-layers-plus:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Build your own stack</p>
<p>A kit holds your packages, parameters and services on top of a deployment, with one CLI to build, run and restart it.</p>
<a href="kits/create-a-kit/" class="md-button">Create a Kit</a>
</div>

<div class="oak-card" markdown="1">

:material-server-outline:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">Target a platform</p>
<p>Support tiers, AutoSD with Podman and Quadlet, and host requirements.</p>
<a href="platforms/" class="md-button">Platforms</a>
</div>

</div>

## Explore the Docs { .oak-eyebrow }

<div class="oak-link-list" markdown="1">

- [**Overview**](overview.md) — What Open AD Kit is and how it is put together
- [**Glossary**](glossary.md) — The terms these docs use
- [**CLI & Maintenance**](getting-started/cli.md) — Every command, configuration, upgrades and cleanup
- [**Troubleshooting**](getting-started/troubleshooting.md) — Docker, data, GPU, visualizer and network
- [**Integrator Guide**](kits/integrator-guide.md) — The reference for every kit extension point
- [**Components**](components/index.md) — The container images and what each one runs
- [**Container Images & Versioning**](releases/container-images.md) — Tags, versions and what to pin
- [**Releases**](releases/index.md) — What a release ships, promises and proves
- [**Development**](development/index.md) — Build from source, contribute and release

</div>
