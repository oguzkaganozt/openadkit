# Open AD Kit Components

[Open AD Kit](https://autoware.org/open-ad-kit/) offers containers for Autoware Components to simplify the deployment of Autoware and its dependencies. This directory contains scripts to build Component containers.

Detailed instructions on how to deploy the components can be found in the [Open AD Kit Deployments](https://autowarefoundation.github.io/openadkit/deployments/).

### `$BASE_IMAGE`

This is a base image of this Dockerfile. [`ros:humble-ros-base-jammy`](https://hub.docker.com/_/ros/tags?page=&page_size=&ordering=&name=humble-ros-base-jammy) will be given.

### `$AUTOWARE_BASE_IMAGE` (from Dockerfile.base)

This stage performs only the basic setup required for all Autoware images.

### `$AUTOWARE_BASE_CUDA_IMAGE` (from Dockerfile.base)

This stage is built on top of `$AUTOWARE_BASE_IMAGE` and adds the CUDA runtime environment and artifacts.

### `rosdep-depend`

The ROS dependency package list files will be generated.
These files will be used in the subsequent stages:

- `core-common-devel`
- `core-devel`
- `core`
- `universe-common`
- `universe-COMPONENT-devel` (e.g. `universe-sensing-perception-devel`)
- `universe-COMPONENT` (e.g. `universe-sensing-perception`)
- `universe-devel`
- `universe`

By generating only the package list files and copying them to the subsequent stages, the dependency packages will not be reinstalled during the container build process unless the dependency packages change.

### `core-common-devel`

This stage installs the dependency packages based on `/rosdep-core-common-depend-packages.txt` and builds the packages under the `core` directory of `autoware.repos` except for `autoware_core`.

### `core-devel`

This stage installs the dependency packages based on `/rosdep-core-depend-packages.txt` and builds the `autoware_core` packages.

### `core`

This stage is an Autoware Core runtime container. It only includes the dependencies given by `/rosdep-core-exec-depend-packages.txt` and the binaries built in the `core-devel` stage.

### `universe-common-devel`

This stage installs the dependency packages based on `/rosdep-universe-common-depend-packages.txt` and builds the packages under the following directories of `autoware.repos`:

- `universe/external`
- `universe/autoware_universe/common`
- `middleware/external`

### `universe-common-devel-cuda`

This stage is built on top of `universe-common-devel` and installs the CUDA development environment.

### `universe-sensing-perception-devel`

This stage installs the dependency packages based on `/rosdep-universe-sensing-perception-depend-packages.txt` and builds the non-CUDA related packages under the following directories of `autoware.repos`:

- `universe/autoware_universe/perception`
- `universe/autoware_universe/sensing`

### `universe-sensing-perception-devel-cuda`

This stage copies the non-CUDA related binaries built in the `universe-sensing-perception-devel` stage and builds the CUDA related packages under the following directories of `autoware.repos`:

- `universe/autoware_universe/perception`
- `universe/autoware_universe/sensing`

### `universe-sensing-perception`

This stage is an Autoware Universe Sensing/Perception runtime container. It only includes the dependencies given by `/rosdep-universe-sensing-perception-exec-depend-packages.txt` and the binaries built in the `universe-sensing-perception-devel` stage.

### `universe-sensing-perception-cuda`

This stage installs the CUDA runtime environment and copies the binaries built in the `universe-sensing-perception-devel-cuda` stage.

### `universe-visualization-devel`

This stage installs the dependency packages based on `/rosdep-universe-visualization-depend-packages.txt` and builds the visualization packages.

### `universe-visualization`

This stage is a Autoware Universe Visualization runtime container. It only includes the dependencies given by `/rosdep-universe-visualization-exec-depend-packages.txt` and the binaries built in the `universe-visualization-devel` stage.

### `universe-localization-mapping-devel`

This stage installs the dependency packages based on `/rosdep-universe-localization-mapping-depend-packages.txt` and builds the packages under the following directories of `autoware.repos`:

- `universe/autoware_universe/localization`
- `universe/autoware_universe/map`

### `universe-localization-mapping`

This stage is an Autoware Universe Localization/Mapping runtime container. It only includes the dependencies given by `/rosdep-universe-localization-mapping-exec-depend-packages.txt` and the binaries built in the `universe-localization-mapping-devel` stage.

### `universe-planning-control-devel`

This stage installs the dependency packages based on `/rosdep-universe-planning-control-depend-packages.txt` and builds the packages under the following directories of `autoware.repos`:

- `universe/autoware_universe/control`
- `universe/autoware_universe/planning`

### `universe-planning-control`

This stage is an Autoware Universe Planning/Control runtime container. It only includes the dependencies given by `/rosdep-universe-planning-control-exec-depend-packages.txt` and the binaries built in the `universe-planning-control-devel` stage.

### `universe-vehicle-system-devel`

This stage installs the dependency packages based on `/rosdep-universe-vehicle-system-depend-packages.txt` and builds the packages under the following directories of `autoware.repos`:

- `universe/autoware_universe/vehicle`
- `universe/autoware_universe/system`

### `universe-vehicle-system`

This stage is an Autoware Universe Vehicle/System runtime container. It only includes the dependencies given by `/rosdep-universe-vehicle-system-exec-depend-packages.txt` and the binaries built in the `universe-vehicle-system-devel` stage.

### `universe-api-devel`

This stage installs the dependency packages based on `/rosdep-universe-api-depend-packages.txt` and builds the API packages.

### `universe-api`

This stage is a Autoware Universe API runtime container. It only includes the dependencies given by `/rosdep-universe-api-exec-depend-packages.txt` and the binaries built in the `universe-api-devel` stage.

### `universe-devel`

This stage installs the dependency packages based on `/rosdep-universe-depend-packages.txt` and copies the binaries built in the following stages:

- `universe-sensing-perception-devel`
- `universe-localization-mapping-devel`
- `universe-planning-control-devel`
- `universe-vehicle-system-devel`
- `universe-visualization-devel`
- `universe-api-devel`

Then it builds the remaining packages of `autoware.repos`:

- `launcher`
- `param`
- `sensor_component`
- `sensor_kit`
- `universe/autoware_universe/evaluator`
- `universe/autoware_universe/launch`
- `universe/autoware_universe/simulator`
- `universe/autoware_universe/tools`
- `vehicle`

This stage provides an all-in-one development container to Autoware developers. By running the host's source code with volume mounting, it allows for easy building and debugging of Autoware.

### `universe-devel-cuda`

This stage installs the CUDA development environment and copies the binaries built in the `universe-sensing-perception-devel-cuda` stage to the `universe-devel` stage.

### `universe`

This stage is an Autoware Universe runtime container. It only includes the dependencies given by `/rosdep-exec-depend-packages.txt` and the binaries built in the `universe-devel` stage.

### `universe-cuda`

This stage installs the CUDA runtime environment and copies the binaries built in the `universe-devel-cuda` stage.
