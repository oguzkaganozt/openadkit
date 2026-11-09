# Roadmap

Last reviewed: 2026-11-09, before v2.0.0.

What Open AD Kit plans next. Finished work leaves this page and appears in the
[release notes](https://github.com/autowarefoundation/openadkit/releases).

## Now: v2.0.0

1. **Release.** A full build and evidence run, then a clean-host install, kit,
   restart and upgrade check on a release candidate.

## Next: v2.x, in priority order

1. **One resolved configuration.** Resolve settings and the Compose model once;
   data paths, images, mounts and validation use the same result.
2. **Development tooling.** A devcontainer and a debugging guide for the
   development loop.
3. **Comparable regression results.** A fixed scenario set whose latency,
   resource use and driving metrics are compared with a baseline.
4. **Platform evidence.** Native arm64 evidence cells and GPU logging simulation
   coverage.
5. **Autoware upgrades.** Measure clean common-image builds on a 4-vCPU runner
   before the next Autoware version change.
6. **Image SBOMs.** A software bill of materials for each container image.
7. **Autoware main canary.** A weekly, non-blocking build against Autoware
   `main`, kept out of releases and PR checks.
8. **Upstream build fixes.** Propose upstream the dependency fixes that the
   image boundaries need.
9. **CES 2027 demo.** Hardware integration and partner evidence for the
   demonstrated setup; tracked in
   [#169](https://github.com/autowarefoundation/openadkit/issues/169).

## Later: direction, not commitment

- **Autoware System Designer.** It selects launch files and parameters; Open AD
  Kit selects images and Compose services. See
  [Autoware System Designer](https://github.com/autowarefoundation/autoware_system_designer).
- **Path to a vehicle.** A vehicle-interface contract and reference hardware, a
  validation ladder from SIL to full-scale vehicles, and offline OCI delivery.
- **Visualizer.** KasmVNC in place of TigerVNC, noVNC and Openbox; Lichtblick
  with `foxglove_bridge` for analysis and bag playback.
- **rmw_zenoh.** Replace `zenoh-bridge-ros2dds` for split-host on Jazzy if an
  evaluation succeeds.
- **Per-image trimming.** Packages that no catalog deployment runs and that
  bring heavy dependencies, such as PyTorch for control's smart MPC,
  calibration tools and DNN packages in CPU images, at the next major version.
- **Safety Island on CARLA.** A kit with the Safety Island's closed loop over
  CAN, backed by its own runtime evidence.

## Non-goals

No custom OTA service, Kubernetes stack, fork of upstream workloads, or ASIL or
NCAP certification claim. Safety Island owns its safety boundary; Open AD Kit
integrates it.

## Keeping This Page Current

- The pull request that finishes an item removes it.
- Each minor or major release reviews the page: items move from Next to Now,
  Later is pruned, and the review line above names the release. Release
  validation stops a minor or major release, and its candidates, until it does.
- An item stays one or two lines; one that needs more links to its issue.
- The order reflects engineering priority, not dates or certification
  commitments.
