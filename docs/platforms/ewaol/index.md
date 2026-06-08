# EWAOL

!!! abstract ""
    EWAOL is a standards-based, container-centric framework for deploying and orchestrating edge workloads. It is the reference implementation for SOAFEE and extends cloud-native methods to automotive with an emphasis on real-time execution and functional safety.

## Status

<span class="oak-badge oak-badge--supported">Documented</span> <span class="oak-badge oak-badge--verified">Verified in v3.0</span>

EWAOL is an actively supported platform in the Open AD Kit ecosystem. The official Open AD Kit v3.0 documentation provides step-by-step build, flash, and runtime instructions for the ADLink AADP-AVA platform.

While this repository is progressively adding EWAOL-specific deployment assets and container orchestration files, the platform itself is fully documented and tested upstream.

## What is EWAOL?

EWAOL is delivered via the `meta-ewaol` Yocto layer and organizes the stack into three layers:

1. **User-defined containerized workloads** — Deployed by end users (e.g., Open AD Kit components)
2. **EWAOL Linux filesystem** — Core services including Docker, K3s, and Xen virtualization
3. **Platform-specific system software** — Firmware, bootloader, OS, and optional Xen hypervisor

It provides runtime parity between edge hardware (ADLink AVA with Ampere Altra / Arm Neoverse N1) and cloud instances (AWS Graviton), making it ideal for hybrid development and deployment workflows.

## Key Capabilities

- **Container-native runtime** with Docker and K3s orchestration
- **Real-time Linux** with deterministic scheduling for safety-critical workloads
- **Virtualization support** via Xen for mixed-criticality separation
- **Yocto-based build system** using `kas` for reproducible image generation
- **Cloud-to-edge parity** with Arm Neoverse N1 architecture on both AVA and AWS Graviton

## Build Overview

The Open AD Kit v3.0 EWAOL workflow uses `kas` to build Yocto images:

```bash
# Clone the Open AD Kit v3.0 EWAOL configuration
# Build the image with kas
kas build kas/ewaol-ava.yml
```

The build produces a bootable image that can be flashed to the AVA platform. After boot, Autoware components run as containerized workloads under K3s.

## Documentation

For the complete EWAOL installation and runtime guide, see the official Open AD Kit v3.0 documentation:

- [Open AD Kit v3.0 Installation Guide](https://autowarefoundation.github.io/open-ad-kit-docs/openadkit_v3/version-3.0/start-guide/installation/)
- [EWAOL User Guide](https://ewaol.docs.arm.com/en/kirkstone-dev/user_guide/reproduce.html)

## Tested Platform

| Platform | Architecture | Status |
|----------|--------------|--------|
| ADLink AADP-AVA | Arm64 (Ampere Altra, Neoverse N1) | Verified |
| AWS EC2 Graviton | Arm64 (Neoverse N1 equivalent) | Runtime parity confirmed |

## Related

- [Supported Platforms overview](../index.md)
- [AutoSD platform](../autosd/index.md)

<!-- DIAGRAM PLACEHOLDER:
     Description: EWAOL Build Pipeline diagram
     Style: Dark navy background (#0a0e27), geometric nodes, blue-green gradient connectors on active paths
     Content: Yocto kas configuration → build → flash AVA → boot → K3s cluster → Autoware containers
     Dimensions: 800x400px, SVG preferred
-->
