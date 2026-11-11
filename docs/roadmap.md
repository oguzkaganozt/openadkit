# Roadmap

What Open AD Kit plans next, as outcomes its users will notice. **Now** is in
progress, **Next** is planned in priority order, and **Later** is direction
without commitment. Finished work moves to the
[release notes](https://github.com/autowarefoundation/openadkit/releases);
maintenance and CI work lives in
[GitHub Issues](https://github.com/autowarefoundation/openadkit/issues).

## Now: v2.0.0

The first stable release: a full build and evidence run, then a clean-host
install, kit, restart and upgrade check on a release candidate.

## Next: v2.x

| Item | What you get |
|------|--------------|
| **Development tooling** | A devcontainer and a debugging guide for the development loop |
| **The base from a kit** | Run a kit's unmodified base deployment from the kit, with the release it pins, to tell the kit's changes from the base |
| **Two levels of base** | A kit on a deployment that has a base itself, such as Safety Island Simulation |
| **Comparable regression results** | A fixed scenario set whose latency, resource use and driving metrics are compared with a baseline |
| **Platform evidence** | Native arm64 evidence cells; a readiness check and an evidence cell for Logging Simulation on CPU; GPU coverage for Logging Simulation |
| **Image SBOMs** | A software bill of materials for each container image |
| **CES 2027 demo** | Hardware integration and partner evidence for the demonstrated setup ([#169](https://github.com/autowarefoundation/openadkit/issues/169)) |

## Later

| Item | What it would bring |
|------|---------------------|
| **Path to a vehicle** | A vehicle-interface contract and reference hardware, a validation ladder from SIL to full-scale vehicles, and offline OCI delivery |
| **Autoware System Designer** | Work with [Autoware System Designer](https://github.com/autowarefoundation/autoware_system_designer), which selects launch files and parameters where Open AD Kit selects images and Compose services |
| **Safety Island on CARLA** | A kit with the Safety Island's closed loop over CAN, backed by its own runtime evidence |
| **Visualizer** | KasmVNC in place of TigerVNC, noVNC and Openbox, at the next major version; Lichtblick with `foxglove_bridge` for analysis and bag playback |
| **rmw_zenoh** | A replacement for `zenoh-bridge-ros2dds` in split-host on Jazzy, if an evaluation succeeds |
| **Smaller images** | Images without the packages that no catalog deployment runs and that bring heavy dependencies, such as PyTorch for control's smart MPC, calibration tools and DNN packages in CPU images; a minor release whose notes list them |
| **One layering mechanism** | One rule in place of three: GPU modes, deployments on a base and split-host nodes each add differences to a stack in their own way. The old ones would go only at a major version |
| **Manifests without `kind`** | An optional `kind`, since `extends` already marks a kit and `version` a release; manifests that carry it are still read |
| **EWAOL** | A decision: the SOAFEE reference implementation becomes a target with a deployment validated on it, or leaves the [support matrix](platforms/index.md#support-matrix) |

## Non-goals

No custom OTA service, Kubernetes stack, fork of upstream workloads, or ASIL or
NCAP certification claim. Safety Island owns its safety boundary; Open AD Kit
integrates it.

Last reviewed: 2026-11-11, before v2.0.0.
