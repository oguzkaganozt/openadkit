# Supported Platforms

[Deployments](../deployments/index.md) run on Ubuntu with Docker Compose, for
development and simulation. **Platforms** are edge targets on automotive
operating systems such as AutoSD.

Open AD Kit is the first [SOAFEE](https://www.soafee.io/) blueprint, co-developed
with SOAFEE and the [eSync Alliance](https://esyncalliance.org/); DENSO's AVP
blueprint and Red Hat's AutoSD blueprint build on it.

<div class="oak-card-grid" markdown="1">

<div class="oak-card" markdown="1">

:material-server:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">AutoSD</p>
<p>The upstream preview of Red Hat In-Vehicle OS. Containers run under Podman and systemd with mixed-criticality partitions.</p>
<a href="autosd/" class="md-button md-button--primary">AutoSD</a>
</div>

<div class="oak-card" markdown="1">

:material-cloud-outline:{ .oak-card-icon }

<p class="oak-card-title" role="heading" aria-level="3">EWAOL</p>
<p>Arm's container-centric Yocto framework and the original SOAFEE reference. Background only; not an Open AD Kit target.</p>
<a href="ewaol/" class="md-button">EWAOL</a>
</div>

</div>

## Support Matrix

A **supported** path is built and shipped by every release and covered by
[Compatibility](../releases/compatibility.md); the notes say where CI evidence
does not reach it. An **experimental** one works but may change in a minor
release. An **unsupported** one is not built or tested here.

A path that fails its build or validation gate is dropped or marked here, not
documented as if it worked. Host requirements and boards are on the
[Hardware](hardware/index.md) page.

| Path | Tier | Notes |
|------|------|-------|
| Ubuntu 22.04 and 24.04 + Docker Compose deployments | **Supported** | Compose validated in CI; CARLA Simulation runs on 22.04 only |
| Component images, amd64 + arm64 | **Supported** | Built and scanned for both; the evidence cells run on amd64. `sensing-perception-cuda` and `planning-cuda` are amd64-only; only the amd64 `simulator` carries the CARLA client |
| Jazzy images | **Supported** | A release needs the Humble and the Jazzy evidence cells to pass; Humble is the default |
| CARLA Simulation | **Supported** | Humble, amd64, NVIDIA GPU; exempt from CI evidence, checked by hand |
| AutoSD with Podman and Quadlet | **Experimental** | Component images, generated from Compose; Planning Simulation only |
| EWAOL | **Unsupported** | No assets in this repository |

Other Linux distributions may work but are not tested.
