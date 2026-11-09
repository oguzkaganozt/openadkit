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

The next priority is to make the existing development workflow simpler and
better verified. Planned work below is not a release date, external team
approval or vehicle certification claim.

### Before v2.0

Implemented in source; these items do not imply a published stable release.

| Area | Completed work |
|------|----------------|
| Releases | Release from `main` on Autoware 2.0.0, with Open AD Kit's own SemVer starting at v2.0.0; require passing evidence for the promoted build and retain provenance. |
| Image selection | One moving alias per image and distro; `openadkit.json` selects the default distro. |
| Developer workflow | `new`, `build -- <colcon args>`, `run --ws`, `restart`, `shell`, deployment paths and `run.json`; find the running stack from any directory. |
| Kits and readiness | Remove the static overlay-contract check and shorten the integrator guide; wait for healthchecks on `run` and `restart`, and expose CI's end-to-end check through `run --verify`. |
| Planner choice | Separate planning and control images; experimental `planning-simulation --gpu` uses Diffusion Planner, its model and diagnostics graph through `planning-cuda`. |
| Split-host | Visualizer on the simulator node; bridge Autoware outputs and the vector map; check the bridge allowlist in CI. |
| Safety Island | Planning Simulation driven by a pinned Safety Island release over `domain_bridge`, with its own evidence cell. |
| AutoSD and boards | Generate Quadlet units from Compose for Planning Simulation; move R-Car X5H board support to its own repository. |

### After v2.0

All items below are planned. Start with the core workflow before expanding
integrations.

#### Core workflow — first priority

- **One resolved configuration:** prepare deployment settings and the Compose
  model in one CLI flow. Data paths, images, mounts and validation should use
  the same resolved result, preserving Compose's interpolation and override rules.
- **Consistent readiness:** give `run` and `restart` a shared readiness and
  failure policy, including healthchecks, crashes and one-shot services. Keep
  restart usable from any directory against the running stack.
- **Verified development loop:** extend the example kit's CI check to edit a ROS
  package, build it, restart the affected services and verify the changed
  behaviour. Add a devcontainer and a debugging guide for this workflow.
- **Comparable regression results:** use a small, fixed scenario set and record
  component latency, resource use and relevant driving metrics such as tracking
  error and jerk. Extend the existing `run.json` and evidence outputs to compare
  results with a baseline under the same test conditions.

#### Runtime evidence and vehicle integration

- **Platform evidence:** run native arm64 runtime cells on hosted arm64 runners
  and add GPU logging simulation coverage.
- **Vehicle integration:** a supported path from simulation to a real vehicle
  interface: a reference hardware deployment where real sensing and vehicle
  services replace the simulator, and a vehicle-interface contract.
- **Validation ladder:** progress from SIL through a virtual vehicle network,
  bench HIL and small-scale vehicles to full-scale vehicles, replacing the
  vehicle node rather than the application.
- **Vehicle delivery:** an OCI package of the digest-pinned system and its BOM
  that can be mirrored offline; fleet rollout stays with the integrator's OTA system.
- **CES 2027 demo:** hardware integration and partner evidence, scoped to the
  demonstrated setup rather than general vehicle support.

#### Integration and visualization

- **Visualizer:** RViz stays the first-class view, with Autoware's own panels
  and tools. Evaluate KasmVNC as a replacement for TigerVNC, noVNC and Openbox;
  add Lichtblick with `foxglove_bridge` for analysis, plots and bag playback.
- **rmw_zenoh:** evaluate it for split-host on Jazzy; replace
  `zenoh-bridge-ros2dds` if the evaluation succeeds. Humble needs a launch patch.
- **Safety Island on CARLA:** a kit with the Safety Island's closed loop over
  CAN, backed by its own runtime evidence because hosted CI cannot run CARLA.
- **Autoware System Designer:** define how Open AD Kit relates to
  [Autoware System Designer](https://github.com/autowarefoundation/autoware_system_designer),
  which selects launch files and parameters, while Open AD Kit selects images
  and Compose services. Make the deployment responsibilities clear.

#### Build and release maintenance

- **Autoware upgrades:** measure clean builds of the common images on a 4-vCPU
  runner and size job limits or runners before the next Autoware version change.
- **Autoware main canary:** a weekly, non-blocking build against Autoware `main`
  to detect upstream breaks early. Keep its images out of releases and PR checks.
- **Image SBOMs:** publish a software bill of materials for the container images.

### Non-goals

No custom OTA service, Kubernetes stack, fork of upstream workloads, or ASIL or
NCAP certification claim. Safety Island owns its safety boundary; Open AD Kit
integrates it.
