# Compatibility

Open AD Kit follows [Semantic Versioning](https://semver.org/) from v2.0.0.
This page lists what that promise covers. Within one major version:

- **A patch release** (`v2.0.1`) fixes bugs and keeps every item below working.
- **A minor release** (`v2.1.0`) adds features and may move to a newer Autoware
  release. It keeps every item below working. JSON output and manifests can
  gain new fields, which readers should ignore.
- **A major release** (`v3.0.0`) is the only one that removes or changes an item
  below. Its release notes list each change under **Breaking changes**.

[Experimental](#experimental) features and what is
[not covered](#not-covered) can change in any release.

## Covered

### CLI

- The commands and options in `openadkit --help` and `openadkit <command> --help`.
- Exit status:

    | Status | Meaning |
    |--------|---------|
    | `0` | Success |
    | `1` | Failure, with an `error:` line on stderr |
    | `2` | Usage error, such as a missing deployment name |
    | `130` | Interrupted |

    `run --verify` exits with the verify step's own status.

- Machine-readable output: `list --json`, `version --json`, `validate --json`
  and each run's `results/run.json`. Each carries `schemaVersion`.

### Manifests

- The kit manifest `openadkit.json` and the deployment manifest
  `deployment.json` at `schemaVersion: 2`: their fields and what they mean.
  A deployment is named by its key in the kit manifest.

### Kits

What a kit made with `openadkit new` builds on:

- `extends` pinning a release, and `base` naming one of its deployments.
- The Compose variables `OPENADKIT_BASE_ROOT`, `OPENADKIT_BASE_DEPLOYMENT` and
  `OPENADKIT_OVERLAY_WS`.
- Each base deployment's Compose entrypoints, service names, data destination
  variables (such as `MAP_PATH`), verify step and the settings listed under
  [Settings and Paths](#settings-and-paths).
- Config overrides under `config/` and the overlay workspace in `overlay_ws/`,
  which the images' entrypoint applies and sources on every start.
- `externalImages` that replace a component image or add new ones.

See [Create a Kit](../kits/create-a-kit.md) and the
[Kit Guide](../kits/kit-guide.md).

### Settings and Paths

- `OPENADKIT_VERBOSE`, `OPENADKIT_INSTALL_DIR`, `OPENADKIT_CONFIG_DIR` and
  `OPENADKIT_OUTPUT_DIR`.
- The host settings file `~/.config/openadkit/<deployment>.env`, and the
  `results` and `recordings` directories under the output directory.
- These settings of a deployment's `settings.env` and of the host settings
  file: the data destination variables, `VEHICLE_MODEL`, `SENSOR_MODEL`,
  `VEHICLE_ID`, `CYCLONEDDS_NETWORK_INTERFACE`, and the visualizer's
  `REMOTE_DISPLAY`, `REMOTE_PASSWORD`, `RVIZ_CONFIG`, `RVIZ_GPU`,
  `WEBSOCKIFY_BIND`, `NOVNC_CERT` and `NOVNC_KEY`.

See [CLI & Maintenance](../getting-started/cli.md).

### Images

- Component image names and the tag scheme: release tags, latest aliases and
  the devel image a kit builds its overlay in. See
  [Container Images & Versioning](container-images.md).
- The image labels `org.opencontainers.image.autoware-base-version` and
  `org.opencontainers.image.ros-snapshot`.
- The Autoware packages that the catalog deployments run and that each image's
  launch files in [Components](../components/index.md) need, with RViz plugins
  in the visualizer image only. They change only with the pinned Autoware
  release: when Autoware removes a package, the minor release that moves to
  that Autoware release says so. An image may lose any other package in a minor
  release, whose notes list it.

### Releases

- The versionless installer and its `install`, `upgrade`, `uninstall` and
  `setup` commands.
- The `openadkit-vX.Y.Z.tar.gz` bundle, and the fields of
  `release-metadata.json` and `release-plan.json`.

## Experimental

These work and are tested where the docs say so, but may change in a minor
release:

- **Split-host nodes:** `--node`, `nodes` in `deployment.json` and the Zenoh
  bridge. See [Split-host Simulation](../deployments/split-host.md).
- **AutoSD with Podman and Quadlet:** `platforms/autosd/` and the units it
  generates. See [AutoSD](../platforms/autosd.md).
- **The Diffusion Planner:** `planning-simulation --gpu`. With Autoware 2.0.0
  its verify step fails on the sample route. See
  [Planning Simulation](../deployments/planning-simulation.md#gpu-mode).

## Not Covered

- Human-readable output: messages, tables and their wording.
- The output of `openadkit config`, which is Docker Compose's resolved model.
- The CI workflows and everything under `.github/`.
- The other settings in `settings.env`. Most are arguments of Autoware's launch
  files and follow the pinned Autoware release; `READINESS_CHECKS` holds the
  arguments of the readiness check.
- Environment variables, files and image internals that this page does not list.
