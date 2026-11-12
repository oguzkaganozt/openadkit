# Glossary

The terms these docs use, one per concept. Each links to the page that covers
it.

## Images

| Term | Meaning |
|------|---------|
| [**Component image**](components/index.md) | A published container image holding one or more Autoware functions, for example `planning`. |
| [**Latest alias**](releases/container-images.md#tag-reference) | An image tag such as `planning-humble` that follows the newest stable release. Release tags (`-vX.Y.Z`) and digests never move. |
| [**Digest pin**](releases/container-images.md#choosing-a-tag) | An image reference by content hash (`@sha256:…`) instead of a tag, so the same image bits are always used. |

## Deployments

| Term | Meaning |
|------|---------|
| [**Deployment**](deployments/index.md) | A named, ready-to-run stack for one task, such as Planning Simulation: a deployment manifest, settings and Compose files. |
| **Deployment manifest** | `deployment.json`: what the CLI needs to run a deployment. Compose files, requirements, data downloads, one-shot services and the verify step. |
| [**Settings**](getting-started/cli.md#configuration) | `KEY=value` variables a deployment runs with, mostly Autoware launch arguments and host paths such as `MAP_PATH`: `settings.env`, then `settings.gpu.env` with `--gpu`, then the host settings file. `run` and `restart` apply them. |
| [**Node**](deployments/split-host.md) | One host's part of a split-host deployment, with its own services, Compose project, ROS domain and Zenoh endpoint. |

## Kits

| Term | Meaning |
|------|---------|
| [**Kit**](kits/create-a-kit.md) | A kit manifest and its deployments: the reference kit in this repository, or your differences on top of a pinned release. |
| [**Kit manifest**](kits/integrator-guide.md#pin-the-base) | `openadkit.json`: what the kit extends, its deployments (each named by its key) and the images it pins. |
| [**`extends` / `base`**](kits/integrator-guide.md#base-a-deployment) | The Open AD Kit release a kit pins, and the deployment of that release a kit deployment builds on. |
| [**Config override**](kits/integrator-guide.md#2-config-overrides) | Parameter and file differences under `config/autoware/`, merged over a package's configuration on every start; not a copy of the full file. `restart` applies them. |
| [**Overlay workspace**](kits/integrator-guide.md#3-overlay-workspace) | Your ROS packages in `overlay_ws/`, built in the release's devel image and sourced on top of Autoware. |
| [**Reference Design**](kits/reference-designs.md) | An Autoware Reference Design: a Deployment Profile and a Reference Software Stack that others can reproduce. A kit holds its software stack. |

## Releases and Evidence

| Term | Meaning |
|------|---------|
| [**Evidence cell**](releases/evidence.md#cells-and-levels) | One runtime test of a deployment on one ROS distro and topology, such as `planning-simulation-humble-linux-amd64`. |
| [**Evidence**](releases/evidence.md) | The evidence cells run against one build. A release needs a run in which every cell passed. |
| [**CI exemption**](releases/evidence.md#ci-exemptions) | A reasoned manifest entry for a deployment without a hosted evidence cell. It is not a passing test. |
| [**BOM**](releases/index.md) | A release's bill of materials: the pinned Autoware release, component images and external images. |

## Platforms

| Term | Meaning |
|------|---------|
| [**Mixed criticality**](platforms/index.md) | Running safety-critical and non-critical workloads on separately qualified execution environments. Here, the Safety Island's real-time hardware beside the containerized stack; the containers on one host share its network and are not isolated by criticality. |
