# AutoSD + Planning + Simulator

!!! abstract ""
    This deployment demonstrates how to run and validate Autoware planning and simulation workflows inside AutoSD using systemd-managed containers (Quadlet) and Podman.

## Folder Structure

| Folder | Contents |
|--------|----------|
| `aib` | Automotive Image Builder manifest files to build an AutoSD OS image |
| `components` | Quadlet service files to run Open AD Kit containers inside AutoSD |
| `docs` | Architecture diagrams and supplementary documentation |

## Workflow

1. Build an AutoSD image with the Automotive Image Builder using the manifests in `aib/`
2. Boot the image on QEMU or target hardware
3. The Quadlet service definitions in `components/` automatically start the Open AD Kit planning and simulator containers via Podman
4. Access the visualizer via the exposed noVNC endpoint

## Related

- [AutoSD Platform Overview](../index.md)
- [Open AD Kit Deployments](../../../deployments/index.md)
- [Components Overview](../../../components/index.md)

<!-- DIAGRAM PLACEHOLDER:
     Description: AutoSD Planning-Simulator Container Topology
     Style: Shows AutoSD host with systemd/Quadlet spawning Podman containers: planning-control, simulator, visualizer
     Blue-green accent on the Quadlet → container orchestration arrows
     Dimensions: 800x350px, SVG preferred
-->
