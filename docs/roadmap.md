# Roadmap

Last reviewed: 2026-11-09, before v2.0.0.

What Open AD Kit plans next, as outcomes its users will notice. Finished work
leaves this page and appears in the
[release notes](https://github.com/autowarefoundation/openadkit/releases).
Maintenance and CI work is tracked in
[GitHub Issues](https://github.com/autowarefoundation/openadkit/issues), not
here.

## Now: v2.0.0

1. **The first stable release.** A full build and evidence run, then a
   clean-host install, kit, restart and upgrade check on a release candidate.

## Next: v2.x, in priority order

1. **Development tooling.** A devcontainer and a debugging guide for the
   development loop.
2. **The base from a kit.** Run a kit's unmodified base deployment from the
   kit, with the release it pins, to tell the kit's changes from the base.
3. **Two levels of base.** A kit on a deployment that has a base itself, such
   as Safety Island Simulation.
4. **Comparable regression results.** A fixed scenario set whose latency,
   resource use and driving metrics are compared with a baseline.
5. **Platform evidence.** Native arm64 evidence cells, a readiness check and
   an evidence cell for Logging Simulation on CPU, and GPU logging simulation
   coverage.
6. **Image SBOMs.** A software bill of materials for each container image.
7. **CES 2027 demo.** Hardware integration and partner evidence for the
   demonstrated setup; tracked in
   [#169](https://github.com/autowarefoundation/openadkit/issues/169).

## Later: direction, not commitment

- **Autoware System Designer.** It selects launch files and parameters; Open AD
  Kit selects images and Compose services. See
  [Autoware System Designer](https://github.com/autowarefoundation/autoware_system_designer).
- **Path to a vehicle.** A vehicle-interface contract and reference hardware, a
  validation ladder from SIL to full-scale vehicles, and offline OCI delivery.
- **EWAOL.** Decide whether the SOAFEE reference implementation, now kept by
  the SOAFEE SIG, becomes a target with a deployment validated on it, or
  leaves the [support matrix](platforms/index.md#support-matrix).
- **Visualizer.** KasmVNC in place of TigerVNC, noVNC and Openbox, at the next
  major version; Lichtblick with `foxglove_bridge` for analysis and bag
  playback.
- **rmw_zenoh.** Replace `zenoh-bridge-ros2dds` for split-host on Jazzy if an
  evaluation succeeds.
- **Per-image trimming.** Packages that no catalog deployment runs and that
  bring heavy dependencies, such as PyTorch for control's smart MPC,
  calibration tools and DNN packages in CPU images, in a minor release whose
  notes list them.
- **One layering mechanism.** GPU modes, deployments on a base and split-host
  nodes each add differences to a stack by rules of their own; one mechanism
  could replace the three. It would come beside them in a minor release, and
  the old ones would go only at a major version.
- **Safety Island on CARLA.** A kit with the Safety Island's closed loop over
  CAN, backed by its own runtime evidence.
- **Manifests without `kind`.** `extends` already marks a kit and `version` a
  release, so `kind` repeats them. It could become optional in a minor
  release, with manifests that carry it still read.

## Non-goals

No custom OTA service, Kubernetes stack, fork of upstream workloads, or ASIL or
NCAP certification claim. Safety Island owns its safety boundary; Open AD Kit
integrates it.

## Keeping This Page Current

- An item is an outcome a user will notice. Maintenance, CI and release chores
  go to an issue instead.
- The pull request that finishes an item removes it.
- Each minor or major release reviews the page: items move from Next to Now,
  Later is pruned, and the review line above names the release. Release
  validation stops a minor or major release, and its candidates, until it does.
- An item stays one or two lines; one that needs more links to its issue.
- The order reflects engineering priority, not dates or certification
  commitments.
