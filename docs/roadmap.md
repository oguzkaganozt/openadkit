# Roadmap

Last reviewed: 2026-11-09, before v2.0.0.

What Open AD Kit plans next. Finished work leaves this page and appears in the
[release notes](https://github.com/autowarefoundation/openadkit/releases).

## Now: v2.0.0

1. **Release.** A full build and evidence run, then a clean-host install, kit,
   restart and upgrade check on a release candidate. Before it, review the
   registry cleanup's first list-only run and set `REGISTRY_CLEANUP=delete`;
   after it, delete the `openadkit-common` package, which no build uses since
   every image went to `openadkit`, and remove the pre-release note
   (`docs/includes/first-release-note.md` and the line in `README.md`).

## Next: v2.x, in priority order

1. **One resolved configuration.** Resolve settings and the Compose model once;
   data paths, images, mounts and validation use the same result.
2. **Development tooling.** A devcontainer and a debugging guide for the
   development loop.
3. **The base from a kit.** Run a kit's unmodified base deployment from the
   kit, with the release it pins, to tell the kit's changes from the base.
4. **Two levels of base.** A kit on a deployment that has a base itself, such
   as Safety Island Simulation.
5. **Comparable regression results.** A fixed scenario set whose latency,
   resource use and driving metrics are compared with a baseline.
6. **Platform evidence.** Native arm64 evidence cells, a readiness check and
   an evidence cell for Logging Simulation on CPU, and GPU logging simulation
   coverage.
7. **Autoware upgrades.** Measure clean common-image builds on a 4-vCPU runner
   before the next Autoware version change.
8. **Image SBOMs.** A software bill of materials for each container image.
9. **Autoware main canary.** A weekly, non-blocking build against Autoware
   `main`, kept out of releases and PR checks.
10. **Upstream build fixes.** Propose upstream the dependency fixes that the
    image boundaries need.
11. **Build once, promote.** Build and test a pull request in the merge queue,
    on the commit `main` will get, and copy its images to `main` by digest
    instead of building them again; that build then covers arm64 too.
    Build-tagged images then stay in `openadkit-ci`, and `openadkit` keeps
    releases, latest aliases and the moving tags.
12. **Faster main builds.** Components wait only for their own common images,
    and the evidence does not wait for the CUDA and arm64 images it never runs.
13. **ROS snapshot key.** The snapshot signing key in the images expires on
    2027-06-01; replace it with the extended key before then.
14. **CES 2027 demo.** Hardware integration and partner evidence for the
    demonstrated setup; tracked in
    [#169](https://github.com/autowarefoundation/openadkit/issues/169).

## Later: direction, not commitment

- **Autoware System Designer.** It selects launch files and parameters; Open AD
  Kit selects images and Compose services. See
  [Autoware System Designer](https://github.com/autowarefoundation/autoware_system_designer).
- **Path to a vehicle.** A vehicle-interface contract and reference hardware, a
  validation ladder from SIL to full-scale vehicles, and offline OCI delivery.
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

- The pull request that finishes an item removes it.
- Each minor or major release reviews the page: items move from Next to Now,
  Later is pruned, and the review line above names the release. Release
  validation stops a minor or major release, and its candidates, until it does.
- An item stays one or two lines; one that needs more links to its issue.
- The order reflects engineering priority, not dates or certification
  commitments.
