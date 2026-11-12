# Kit Guide

The reference for a kit: what it pins, each extension point, and how it is
validated and upgraded. A kit owns its differences; Open AD Kit owns the
CLI, the images and the catalog. Start one with `openadkit new`
([Create a Kit](create-a-kit.md)).

## Pin the Release

In the kit's `openadkit.json`, `kind` is `kit` and `extends` names a published
release tag or, for development, the path of a source checkout. Manifests use
`schemaVersion: 2`; older ones are rejected.

- **The pinned release runs the kit.** The CLI finds it under
  `~/.local/share/openadkit/openadkit-<tag>` (`OPENADKIT_INSTALL_DIR` to
  change) and hands the command to its launcher. A missing version is
  downloaded and verified on first use, as a build tool's wrapper does; your
  active `openadkit` stays as it is.
- **Only the commands that act on a kit do this:** `validate`, `config`,
  `fetch`, `run`, `build` and `clean`. `list`, `version`, `new`, every `--help`
  and Tab completion read the kit with the CLI you called, so a directory you
  only look at starts no program and no download.
- **One level of `extends`:** a kit extends Open AD Kit, not another kit.

## Choose a Base Deployment

Each kit deployment names a `base` deployment of the pinned release in its
`deployment.json`.

- **Requirements** (architectures, ROS distros, GPU) are inherited.
  `requirements` may narrow them: fewer architectures or ROS distros, or `gpu`
  set to `none` or `required` where the base leaves it optional. It never
  widens them, since the kit runs the base's services. Without a GPU mode, the
  base's GPU-only downloads are left out.
- **Downloads and one-shot services** are inherited. A kit can add
  downloads with distinct destination variables, and one-shot services of its
  own.
- **Split-host roles are not inherited:** a kit deployment runs on one host.

A kit made by `openadkit new my-kit` has one deployment, also named `my-kit`.
Its manifests, Compose file and differences live in one directory
(`deployments.my-kit.path` is `"."`), so it needs no nested `deployments/`
directory. Run commands from that directory, where they need no deployment
name.

## Extension Points

### 1. Settings

Put only differences in your deployment's `settings.env`. Compose reads these
files in order (later files win):

1. Base `settings.env`
2. Base `settings.gpu.env`, when GPU mode is selected
3. Kit `settings.env`, if present
4. Kit `settings.gpu.env`, if present and GPU mode is selected
5. The host settings file, `~/.config/openadkit/<kit-deployment>.env`, if present

Shell exports do not override values set in these files. The CLI adds the ROS
distro, the host UID and GID, the overlay mount paths, `OPENADKIT_ROOT`
(the release's root) and `OPENADKIT_BASE_DEPLOYMENT` (the directory of the `base`
deployment); a release's component and external images stay pinned. Inside the
containers, the ROS and DDS defaults come from the base services'
`runtime.env`.

### 2. Config Overrides

Store overrides under
`config/autoware/<package>/<path-relative-to-package-share>`. For example,
`config/autoware/autoware_control_config/config/lane_departure_checker/lane_departure_checker.param.yaml`:

```yaml
/**:
  ros__parameters:
    update_rate: 20.0
```

On each start, the entrypoint hook copies the package share directory into
`/tmp/openadkit/<package>/share/<package>`. It applies the base deployment's
layer, then the kit deployment's. YAML mappings merge
recursively; scalars and lists replace the old value. Launch substitutions such
as `$(var ...)` stay intact. Non-YAML files replace their counterpart.

The copied prefixes go first on `AMENT_PREFIX_PATH`, and base launch arguments
use the same stable paths. No change is written into the image. Removing an
override and restarting returns to the remaining layers.

Unknown packages, files or YAML keys are warnings, not startup failures. The
hook logs them and writes `/tmp/openadkit/overlay-report.json` in each container.
Once the services are up, `run` collects those reports and warns about every
override without a counterpart: a package no service has changes nothing, and a
file or a parameter its package does not have is added. That is intended for a
new file such as a diagnostics graph; after a release change it usually
means a renamed package, file or parameter. Every service gets the same layers,
so a package installed in only some images is not reported.

### 3. Overlay Workspace

Put ROS packages in `overlay_ws/src` and build them in the
`universe-common-devel` image from the **same build** as your runtime images.
A release pins that image next to its runtime images, so the CLI builds with
the right one:

```bash
openadkit build [--ros-distro humble]   # in the kit: its overlay_ws
openadkit build PATH                    # any workspace, with the pins of the kit around it
openadkit build -- --packages-select my_pkg                # arguments after -- go to colcon build
openadkit build -- --cmake-args -DCMAKE_BUILD_TYPE=Debug   # Release unless you set another
```

#### Build

- Packages build incrementally: a second build compiles only what changed.
- The CLI records the image and distro in `install/.openadkit-overlay.json`.
  After a release upgrade or a distro change, `validate` and `run` warn until you
  rebuild, and that rebuild starts from a clean `build/` and `install/`, since
  CMake caches record the paths they were configured with.
- `--install-base` and `--build-base` stay fixed: the services source
  `install/` where they mount the workspace.
- A source checkout pins no devel image: set `DEVEL_IMAGE` to the matching
  `universe-common-devel` digest from the build's metadata.

#### Run

The workspace belongs to the kit: the one `overlay_ws` at the kit root serves
every deployment of the kit, since they all extend one release and its images.
Every Autoware service mounts it, and the entrypoint hook sources
`overlay_ws/install/local_setup.bash` on top of Autoware, so its packages are
visible in every service. Whether your code runs depends on what starts it:

- A changed copy of an Autoware package shadows the image's own. It runs where
  Autoware already launches that package, with nothing more to configure;
  Autoware packages that link against its library keep the copy they were
  built with.
- A new node runs only where something starts it: an extra service (as the
  example kit's `acme-probe`), a launch file you override under
  `config/autoware`, or by hand with
  `openadkit shell <service> ros2 run <package> <node>`.

#### Without a Kit

To try a workspace with a catalog deployment, without writing a kit, mount it
with `--ws`:

```bash
openadkit build ~/my_ws
openadkit run planning-simulation --ws ~/my_ws
```

`--ws` is for a deployment without a workspace of its own; on a kit that has
one it is an error rather than a second layer.

#### ABI

The devel and runtime images install ROS packages from the same
[ROS snapshot](../releases/container-images.md#ros-package-snapshot), so
an overlay built in the devel image links the ROS versions the runtime image
ships. A dependency you add must also exist in the runtime image; the overlay
cannot install packages. The example kit's C++ node links `diagnostic_updater`
deliberately to test this devel/runtime boundary, then publishes `/acme/probe`.

### 4. Extra Services

Include the base's Compose file through `OPENADKIT_BASE_DEPLOYMENT`, then
define your services under `services:`. Keep communicating ROS services on the
base ROS domain and middleware, and give each one `init: true`
([Develop and Debug](develop-and-debug.md#the-development-loop)).

An extra Open AD Kit runtime service loads the kit workspace by mounting
`${OPENADKIT_OVERLAY_WS}` at `/openadkit/overlay_ws:ro`, as the example kit's
`acme-probe` does. It needs no image of its own: a runtime image and the
workspace are enough. Build your own image only for what the runtime images
lack, such as a system package or a non-ROS application, and declare it as an
external image ([point 5](#5-image-replacement)).

To replace one role of a base that runs as split-host roles, include only the
other role's Compose file instead of the base's `compose.yaml`. For
example, a kit that brings its own simulator to `carla-simulation` includes
`${OPENADKIT_BASE_DEPLOYMENT}/compose.autoware.yaml`: no service in it depends
on a CARLA service. The base's `oneShotServices` that the kit's services leave
out are skipped; the kit's own must exist.

### 5. Image Replacement

Declare the images your kit uses but does not build in its `externalImages`,
each with either one digest-pinned `ref` or a `distros` map of digest-pinned
references. A name matching a component image variable replaces that
component; other names supply images for new services. Use `${NAME:?}` in
Compose to require the declared reference.

A replaced component image needs your own runtime evidence: pinning alone does not
prove that it honors the entrypoint, launch or parameter interfaces.

## A New Vehicle

Autoware finds a vehicle and its sensors by package name. With
`VEHICLE_MODEL=my_vehicle` and `SENSOR_MODEL=my_sensor_kit`, its launch files
read four packages:

| Package | Holds |
| --- | --- |
| `my_vehicle_description` | `vehicle_info.param.yaml`, the simulator model and the vehicle's URDF and mesh |
| `my_vehicle_launch` | `vehicle_interface.launch.xml`, which starts your vehicle interface |
| `my_sensor_kit_description` | The sensor calibration files and the sensor kit's URDF |
| `my_sensor_kit_launch` | The sensor launch files and the sensor kit's diagnostics configuration |

1. Put the four packages in `overlay_ws/src`. Autoware's
   `sample_vehicle_description`, `sample_vehicle_launch`,
   `sample_sensor_kit_description` and `sample_sensor_kit_launch` are the
   templates: copy them and replace the names in every file.
2. Set `VEHICLE_MODEL` and `SENSOR_MODEL` in `settings.env`.
3. Build and run: `openadkit build`, then `openadkit run --verify`.

Every service sources the workspace, so planning, control, the simulator and
the visualizer all read the same vehicle. All four packages must exist: the
vehicle and system services look up the two `_launch` packages on every start.
`validate` does not check for them. When one is missing, `run` reports the
service that failed, and `openadkit logs <service>` names the package. Every
release tests this path: the example kit drives with four such packages.

Autoware's defaults describe a passenger car. Review these for your vehicle.
The first two are in your packages. The others belong to Autoware packages, so
change them with [config overrides](#2-config-overrides); their package and
path depend on the release's Autoware version, so look them up in its images and
check `run`'s override warnings.

| Parameters | File | Why |
| --- | --- | --- |
| Dimensions, `wheel_base`, `max_steer_angle` | `vehicle_info.param.yaml` of your vehicle description | Planning and control use them as limits; a steering limit above the vehicle's makes control ask for angles it cannot reach. |
| Sensor poses | your sensor kit's `sensor_kit_calibration.yaml` and `sensors_calibration.yaml` | A wrong sign or offset shows up as a localization error of the same size. |
| `nominal_latency`, `assumed_limit_acc` | `control_validator.param.yaml` | Your actuation latency and achievable braking. With car values a slower or weaker vehicle fails validation and triggers an MRM. |
| `pose_measurement.pose_gate_dist` | `ekf_localizer.param.yaml` | The Mahalanobis gate for pose updates. A start pose far from the truth can be rejected for good. |
| Velocity, acceleration, jerk and steering-rate limits | `vehicle_cmd_gate.param.yaml` | The last limits before the vehicle interface. |

## Validation and Evidence

`openadkit validate` renders the deployment and checks its manifest (and, with
`--data`, its data). It does not pull images or prove that the runtime works;
`run` reports overrides without a counterpart (see
[Config Overrides](#2-config-overrides)).

Your kit's acceptance checks run where CI runs its own:

- **Readiness:** give a service of your own a Compose `healthcheck`. `run`
  waits until it passes. The example kit's `acme-probe` service runs
  `checks/example_kit.py`, which checks the fresh `/acme/probe` publication of
  its C++ package and its parameters.
- **End to end:** the base's `verify` step runs on top of your layer with
  `openadkit run --verify`. To check something else, name your own in
  `deployment.json`: `{"verify": {"service": "<service>", "command": [...]}}`
  runs the command in that running service, and without `command` the step
  waits for the service to exit and takes its exit code.

The example kit is what `openadkit new` makes, with a
[fixture](https://github.com/autowarefoundation/openadkit/tree/main/.github/scripts/evidence/example-kit)
that uses every extension point on top. Its evidence cells run both checks on
Humble and Jazzy, each with a workspace built against the matching devel
digest, and every release needs them to pass. They show that the extension
points work on that build; they do not verify your kit.

A base deployment's CI exemption stays with the kit; an exemption is not
runtime evidence. The [evidence workflow](../development/evidence-workflow.md)
does not yet accept external kits.

## Upgrade Without Losing Your Work

Install the new release next to the old one, update `extends`, rebuild your
workspace against its devel digest, then validate and run your acceptance
checks. Your repository, host settings, downloaded data and output directories
are outside the release, and `openadkit upgrade` does not change a kit's
`extends`. See [Settings](../getting-started/cli.md#settings) and
[Downloaded Data](../getting-started/cli.md#downloaded-data).
