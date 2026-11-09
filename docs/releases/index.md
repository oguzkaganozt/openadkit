# Releases & Roadmap

**No stable release has been published yet.** Until the first release, run Open
AD Kit from a [source checkout](../getting-started/index.md).

## Releases

[GitHub Releases](https://github.com/autowarefoundation/openadkit/releases) is
the canonical source for published versions, release notes, and provenance
metadata. Each stable release publishes:

- a versionless `openadkit` installer
- the versioned `openadkit-vX.Y.Z.tar.gz` bundle
- the pinned Autoware meta-release, ROS 2 distro(s), and image tags and digests
- a BOM, the passing runtime evidence summary, explicit CI exemptions and default distro
- build provenance for the installer, bundle, plan and metadata

Installed releases move to the latest stable version with `openadkit upgrade`.
Tag naming is documented in
[Container Images & Versioning](../getting-started/container-images.md).
See [Evidence Policy](evidence.md) for the blocking gate and verification report, and
[Verify a Release](verification.md) before executing downloaded artifacts.

## Roadmap

Completed work comes first, followed by planned work in priority order:
make the existing workflow reliable, simplify its foundations, then expand
platform and vehicle integrations.

### Done

Implemented in source; these items do not imply a published stable release.

- **Releases.** Build releases from `main` pinned to an Autoware release tag,
  with Open AD Kit's own SemVer from v2.0.0; require passing evidence for the
  promoted build and retain provenance.
- **Image selection.** Publish one moving alias per image and distro, and select
  the default distro from `openadkit.json`.
- **Developer workflow.** Provide `new`, `build -- <colcon args>`, `run --ws`,
  `restart`, `shell`, deployment paths and `run.json`, and find the running
  stack from any directory.
- **Kits.** Remove the static overlay-contract check and shorten the integrator
  guide.
- **Readiness.** Wait for healthchecks on `run` and `restart`, and expose CI's
  end-to-end check through `run --verify`.
- **Planner choice.** Split planning and control images; experimental
  `planning-simulation --gpu` uses Diffusion Planner, its model and diagnostics
  graph through `planning-cuda`.
- **Split-host.** Run the visualizer on the simulator node, bridge Autoware
  outputs and the vector map, and check the bridge allowlist in CI.
- **Safety Island.** Drive Planning Simulation from a pinned Safety Island
  release over `domain_bridge`, with its own evidence cell.
- **AutoSD and boards.** Generate Quadlet units from Compose for Planning
  Simulation, and move R-Car X5H board support to its own repository.

### Planned — in priority order

The order reflects engineering priorities, not release dates or certification
commitments.

1. **Consistent readiness.** Replace today's separate `run` and `restart`
    checks with one shared readiness and failure policy for healthchecks,
    crashes and one-shot services. Keep restart usable from any directory
    against the running stack.

2. **Verified development loop.** Extend the example kit's CI check to edit a
    ROS package, build it, restart the affected services and verify the changed
    behaviour. Add a devcontainer and a debugging guide for this workflow.

3. **One resolved configuration.** Prepare deployment settings and the Compose
    model in one CLI flow. Data paths, images, mounts and validation should use
    the same result, preserving Compose's interpolation and override rules.

4. **Component build boundaries.** Review cross-component source mounts and
    package dependencies. Remove unnecessary dependencies, extract genuinely
    shared helpers, and keep domain-specific packages with their owners and
    explicit dependencies. Limit each image to the build inputs and runtime
    packages it needs; propose upstream fixes where needed. Reuse alone should
    not move a package into `common` or add it to every image's base.

5. **Comparable regression results.** Use a small, fixed scenario set and record
    component latency, resource use and relevant driving metrics such as tracking
    error and jerk. Extend `run.json` and evidence outputs to compare results with
    a baseline under the same test conditions.

6. **Platform evidence.** Run native arm64 runtime cells on hosted arm64 runners
    and add GPU logging simulation coverage.

7. **Autoware upgrades.** Measure clean builds of the common images on a 4-vCPU
    runner and size job limits or runners before the next Autoware version change.

8. **Image SBOMs.** Publish a software bill of materials for the container images.

9. **Autoware main canary.** Run a weekly, non-blocking build against Autoware
    `main` to detect upstream breaks early. Keep its images out of releases and
    PR checks.

10. **Autoware System Designer.** Clarify deployment responsibilities with
    [Autoware System Designer](https://github.com/autowarefoundation/autoware_system_designer):
    it selects launch files and parameters, while Open AD Kit selects images
    and Compose services.

11. **Vehicle integration.** Define a vehicle-interface contract and a reference
    hardware deployment where real sensing and vehicle services replace the
    simulator.

12. **Validation ladder.** Progress from SIL through a virtual vehicle network,
    bench HIL and small-scale vehicles to full-scale vehicles, replacing the
    vehicle node rather than the application.

13. **Vehicle delivery.** Package the digest-pinned system and its BOM as an OCI
    artifact that can be mirrored offline. Fleet rollout stays with the
    integrator's OTA system.

14. **CES 2027 demo.** Integrate hardware and collect partner evidence for the
    demonstrated setup, rather than claiming general vehicle support.

15. **Visualizer.** Keep RViz and Autoware's panels as the first-class view.
    Evaluate KasmVNC as a replacement for TigerVNC, noVNC and Openbox; add
    Lichtblick with `foxglove_bridge` for analysis, plots and bag playback.

16. **rmw_zenoh.** Evaluate it for split-host on Jazzy; replace
    `zenoh-bridge-ros2dds` if the evaluation succeeds. Humble needs a launch patch.

17. **Safety Island on CARLA.** Create a kit with the Safety Island's closed loop
    over CAN, backed by its own runtime evidence because hosted CI cannot run CARLA.

### Non-goals

No custom OTA service, Kubernetes stack, fork of upstream workloads, or ASIL or
NCAP certification claim. Safety Island owns its safety boundary; Open AD Kit
integrates it.
