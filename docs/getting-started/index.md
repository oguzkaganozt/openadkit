# Getting Started

This guide walks you through setting up your environment and running your first Open AD Kit deployment.

## Prerequisites

<div class="oak-card-grid">

<div class="oak-card">
<span class="oak-card-icon">:material-docker:</span>
<h3>Docker Engine</h3>
<p>Required for all deployments. Docker Compose is typically included with Docker Desktop.</p>
<a href="https://docs.docker.com/engine/install/" class="md-button" target="_blank">Install Docker</a>
</div>

<div class="oak-card">
<span class="oak-card-icon">:material-gpu:</span>
<h3>NVIDIA Container Toolkit</h3>
<p>Optional but strongly recommended for GPU-accelerated sensing and perception.</p>
<a href="https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html" class="md-button" target="_blank">Install Toolkit</a>
</div>

<div class="oak-card">
<span class="oak-card-icon">:material-package-variant-closed:</span>
<h3>Autoware Artifacts</h3>
<p>Required for sensing and perception deployments such as Logging Simulation.</p>
</div>

</div>

!!! tip "Quick Setup"
    All the above requirements can be installed automatically by running the **`setup.sh`** script included in the repository.

## Installation

<div class="oak-steps">

- **Clone the repository**
  ```bash
  git clone https://github.com/autowarefoundation/openadkit
  cd openadkit
  ```

- **Set up the runtime environment**
  ```bash
  sudo ./setup.sh
  ```
  This installs Docker, NVIDIA Container Toolkit, and other dependencies. It requires sudo privileges.

  !!! tip "Skip NVIDIA Toolkit"
      Use the `--no-nvidia` flag if you do not have an NVIDIA GPU. Otherwise, the toolkit is **highly recommended** for sensing and perception performance.

- **Download Autoware artifacts (if needed)**
  ```bash
  sudo ./setup.sh --download-artifacts
  ```
  Required for deployments that mount `${HOME}/autoware_data`, including the Logging Simulation sample.

</div>

## Verify Your Installation

After running `setup.sh`, confirm your environment is ready:

```bash
# Check Docker
docker --version
docker compose version

# Check NVIDIA toolkit (if installed)
nvidia-ctk --version

# Verify artifacts directory
ls -la ~/autoware_data
```

!!! success "Ready to Deploy"
    If all checks pass, you are ready to run a sample deployment. See [Sample Deployments](../deployments/samples/index.md).

## Reference

- [Container Image Tags](image-tags.md) — Understanding the tag schema for choosing the right image
- [Release Flow](release-flow.md) — How Open AD Kit releases are built, scanned, and promoted

## Next Steps

- [Run your first deployment](../deployments/samples/planning-simulation/index.md) — Start with the Planning Simulation sample
- [Learn about components](../components/index.md) — Understand the Open AD Kit architecture
- [Choose a platform](../platforms/index.md) — Deploy to AutoSD, EWAOL, or your local machine

```mermaid
flowchart LR
    A[Clone Repository] --> B[Run setup.sh]
    B --> C[Verify Installation]
    B -.->|Optional| D[--no-nvidia Flag]
```
