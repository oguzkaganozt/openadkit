# autoware-base/Dockerfile - Unified Dockerfile for all intermediate development stages
# This file consolidates: autoware-base, rosdep, core, autoware-common, and visualization
#
# Build targets:
#   - base / base-cuda: Foundation images
#   - rosdep-depend: Dependency lists (scratch image)
#   - core-devel: Core development image
#   - universe-common-devel / universe-common-devel-cuda: Common universe development images
#   - visualization-devel: Visualization development image
#   - universe-visualization: Visualization runtime image

# =============================================================================
# Global ARGs
# =============================================================================
ARG BASE_IMAGE=ros:humble-ros-base-jammy
ARG ROS_DISTRO=humble
ARG LIB_DIR=x86_64

# =============================================================================
# Stage: base
# Foundation image with ROS and basic development environment
# =============================================================================
# hadolint ignore=DL3006
FROM $BASE_IMAGE AS base
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO

# Copy files
COPY setup-dev-env.sh ansible-galaxy-requirements.yaml amd64.env amd64_jazzy.env arm64.env /autoware/
COPY ansible/ /autoware/ansible/
COPY docker/autoware-base/build_scripts/cleanup_apt.sh /autoware/cleanup_apt.sh
RUN chmod +x /autoware/cleanup_apt.sh
COPY docker/autoware-base/build_scripts/cleanup_system.sh /autoware/cleanup_system.sh
RUN chmod +x /autoware/cleanup_system.sh
WORKDIR /autoware

# Disable installing suggested and recommended packages
RUN echo 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/99-disable-extra-packages; \
    echo 'APT::Install-Suggests "false";' >> /etc/apt/apt.conf.d/99-disable-extra-packages

# Install apt packages and add GitHub to known hosts for private repositories
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
  && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
  gosu \
  ssh \
  && /autoware/cleanup_apt.sh \
  && mkdir -p ~/.ssh \
  && ssh-keyscan github.com >> ~/.ssh/known_hosts

# Set up base environment
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module base --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && /autoware/cleanup_apt.sh \
  && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" > /etc/bash.bashrc

# Create entrypoint
COPY components/autoware-base/etc/ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh
CMD ["/bin/bash"]

# =============================================================================
# Stage: base-cuda
# Base image with CUDA runtime support
# =============================================================================
FROM base AS base-cuda
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO

# Set up CUDA runtime environment
# hadolint ignore=SC2002,SC2086
RUN --mount=type=ssh \
  ./setup-dev-env.sh -y --module base --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && /autoware/cleanup_apt.sh true

# =============================================================================
# Stage: rosdep-base
# Generates all rosdep package dependency lists
# =============================================================================
FROM base AS rosdep-base
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO

COPY docker/autoware-base/resolve_rosdep_keys.sh /autoware/resolve_rosdep_keys.sh
RUN chmod +x /autoware/resolve_rosdep_keys.sh

RUN rm -f /etc/apt/apt.conf.d/docker-clean \
  && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache \
  && /autoware/cleanup_apt.sh

# Generate core-common package lists
COPY src/core/autoware_adapi_msgs /autoware/src/core/autoware_adapi_msgs
COPY src/core/autoware_cmake /autoware/src/core/autoware_cmake
COPY src/core/autoware_internal_msgs /autoware/src/core/autoware_internal_msgs
COPY src/core/autoware_lanelet2_extension /autoware/src/core/autoware_lanelet2_extension
COPY src/core/autoware_msgs /autoware/src/core/autoware_msgs
COPY src/core/autoware_utils /autoware/src/core/autoware_utils
RUN rosdep update && /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-core-common-depend-packages.txt \
  && cat /rosdep-core-common-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-core-common-exec-depend-packages.txt \
  && cat /rosdep-core-common-exec-depend-packages.txt

# Generate core package lists
COPY src/core/autoware_core /autoware/src/core/autoware_core
RUN rosdep update && /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-core-depend-packages.txt \
  && cat /rosdep-core-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-core-exec-depend-packages.txt \
  && cat /rosdep-core-exec-depend-packages.txt

# Generate universe-common package lists
COPY src/universe/external /autoware/src/universe/external
# trt_batched_nms depends on autoware_tensorrt_common and autoware_cuda_utils, which are not available in universe-common stage
RUN rm -rf /autoware/src/universe/external/trt_batched_nms
COPY src/universe/autoware_universe/common /autoware/src/universe/autoware_universe/common
COPY src/middleware/external /autoware/src/middleware/external
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-common-depend-packages.txt \
  && cat /rosdep-universe-common-depend-packages.txt

# Generate visualization package lists
COPY src/universe/autoware_universe/visualization /autoware/src/universe/autoware_universe/visualization
COPY src/core/autoware_rviz_plugins /autoware/src/core/autoware_rviz_plugins
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-visualization-depend-packages.txt \
  && cat /rosdep-universe-visualization-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-universe-visualization-exec-depend-packages.txt \
  && cat /rosdep-universe-visualization-exec-depend-packages.txt

# Generate sensing-perception package lists
COPY src/universe/autoware_universe/launch/tier4_perception_launch /autoware/src/universe/autoware_universe/launch/tier4_perception_launch
COPY src/universe/autoware_universe/launch/tier4_sensing_launch /autoware/src/universe/autoware_universe/launch/tier4_sensing_launch
COPY src/universe/autoware_universe/perception /autoware/src/universe/autoware_universe/perception
COPY src/universe/autoware_universe/sensing /autoware/src/universe/autoware_universe/sensing
COPY src/universe/autoware_universe/evaluator/autoware_perception_online_evaluator /autoware/src/universe/autoware_universe/evaluator/autoware_perception_online_evaluator
COPY src/sensor_component /autoware/src/sensor_component
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-sensing-perception-depend-packages.txt \
  && cat /rosdep-universe-sensing-perception-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-universe-sensing-perception-exec-depend-packages.txt \
  && cat /rosdep-universe-sensing-perception-exec-depend-packages.txt

# Generate localization-mapping package lists
COPY src/universe/autoware_universe/launch/tier4_localization_launch /autoware/src/universe/autoware_universe/launch/tier4_localization_launch
COPY src/universe/autoware_universe/launch/tier4_map_launch /autoware/src/universe/autoware_universe/launch/tier4_map_launch
COPY src/universe/autoware_universe/localization /autoware/src/universe/autoware_universe/localization
COPY src/universe/autoware_universe/map /autoware/src/universe/autoware_universe/map
# TODO(youtalk): Remove COPYs when https://github.com/autowarefoundation/autoware_universe/issues/10282 is resolved
COPY src/universe/autoware_universe/system/autoware_default_adapi_helpers/autoware_automatic_pose_initializer /autoware/src/universe/autoware_universe/system/autoware_default_adapi_helpers/autoware_automatic_pose_initializer
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-localization-mapping-depend-packages.txt \
  && cat /rosdep-universe-localization-mapping-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-universe-localization-mapping-exec-depend-packages.txt \
  && cat /rosdep-universe-localization-mapping-exec-depend-packages.txt

# Generate planning-control package lists
COPY src/universe/autoware_universe/launch/tier4_control_launch /autoware/src/universe/autoware_universe/launch/tier4_control_launch
COPY src/universe/autoware_universe/launch/tier4_planning_launch /autoware/src/universe/autoware_universe/launch/tier4_planning_launch
COPY src/universe/autoware_universe/control /autoware/src/universe/autoware_universe/control
COPY src/universe/autoware_universe/planning /autoware/src/universe/autoware_universe/planning
# TODO(youtalk): Remove COPYs when https://github.com/autowarefoundation/autoware_universe/issues/8805 is resolved
COPY src/universe/autoware_universe/evaluator/autoware_control_evaluator /autoware/src/universe/autoware_universe/evaluator/autoware_control_evaluator
COPY src/universe/autoware_universe/evaluator/autoware_planning_evaluator /autoware/src/universe/autoware_universe/evaluator/autoware_planning_evaluator
COPY src/universe/autoware_universe/vehicle/autoware_external_cmd_converter /autoware/src/universe/autoware_universe/vehicle/autoware_external_cmd_converter
COPY src/universe/autoware_universe/vehicle/autoware_raw_vehicle_cmd_converter /autoware/src/universe/autoware_universe/vehicle/autoware_raw_vehicle_cmd_converter
COPY src/universe/autoware_universe/system/autoware_command_mode_types /autoware/src/universe/autoware_universe/system/autoware_command_mode_types
# diffusion_planner depends on cuda
COPY src/universe/autoware_universe/sensing/autoware_cuda_utils /autoware/src/universe/autoware_universe/sensing/autoware_cuda_utils
COPY src/universe/autoware_universe/perception/autoware_tensorrt_common /autoware/src/universe/autoware_universe/perception/autoware_tensorrt_common
COPY src/universe/autoware_universe/perception/autoware_tensorrt_plugins /autoware/src/universe/autoware_universe/perception/autoware_tensorrt_plugins
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-planning-control-depend-packages.txt \
  && cat /rosdep-universe-planning-control-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-universe-planning-control-exec-depend-packages.txt \
  && cat /rosdep-universe-planning-control-exec-depend-packages.txt

# Generate vehicle-system package lists
COPY src/universe/autoware_universe/launch/tier4_vehicle_launch /autoware/src/universe/autoware_universe/launch/tier4_vehicle_launch
COPY src/universe/autoware_universe/launch/tier4_system_launch /autoware/src/universe/autoware_universe/launch/tier4_system_launch
COPY src/universe/autoware_universe/vehicle /autoware/src/universe/autoware_universe/vehicle
COPY src/universe/autoware_universe/system /autoware/src/universe/autoware_universe/system
# planning_validator and its dependencies
COPY src/core/autoware_core/planning/autoware_planning_factor_interface /autoware/src/core/autoware_core/planning/autoware_planning_factor_interface
COPY src/core/autoware_core/planning/autoware_route_handler /autoware/src/core/autoware_core/planning/autoware_route_handler
COPY src/core/autoware_core/map/autoware_map_height_fitter /autoware/src/core/autoware_core/map/autoware_map_height_fitter
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-vehicle-system-depend-packages.txt \
  && cat /rosdep-universe-vehicle-system-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-universe-vehicle-system-exec-depend-packages.txt \
  && cat /rosdep-universe-vehicle-system-exec-depend-packages.txt

# Generate api package lists
COPY src/universe/autoware_universe/launch/tier4_autoware_api_launch /autoware/src/universe/autoware_universe/launch/tier4_autoware_api_launch
COPY src/universe/autoware_universe/system/autoware_default_adapi_universe /autoware/src/universe/autoware_universe/system/autoware_default_adapi_universe
COPY src/core/autoware_core/api/autoware_adapi_adaptors /autoware/src/core/autoware_core/api/autoware_adapi_adaptors
COPY src/universe/autoware_universe/system/autoware_diagnostic_graph_utils /autoware/src/universe/autoware_universe/system/autoware_diagnostic_graph_utils
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-api-depend-packages.txt \
  && cat /rosdep-universe-api-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-universe-api-exec-depend-packages.txt \
  && cat /rosdep-universe-api-exec-depend-packages.txt

# Generate full universe package lists
COPY src/launcher /autoware/src/launcher
COPY src/universe /autoware/src/universe
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" \
  > /rosdep-universe-depend-packages.txt \
  && cat /rosdep-universe-depend-packages.txt
RUN /autoware/resolve_rosdep_keys.sh /autoware/src "${ROS_DISTRO}" --dependency-types=exec \
  > /rosdep-exec-depend-packages.txt \
  && cat /rosdep-exec-depend-packages.txt

# =============================================================================
# Stage: rosdep-depend
# Final stage with all rosdep package lists (scratch image)
# =============================================================================
FROM scratch AS rosdep-depend
COPY --from=rosdep-base /rosdep-*.txt /

# =============================================================================
# Stage: core-common-devel
# Builds core-common packages
# =============================================================================
FROM base AS core-common-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

COPY docker/autoware-base/build_scripts/build_and_clean.sh /autoware/build_and_clean.sh
RUN chmod +x /autoware/build_and_clean.sh

# Set up development environment and tools
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers openadkit --ros-distro $ROS_DISTRO \
  && ./setup-dev-env.sh -y --module dev-tools openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && /autoware/cleanup_apt.sh

# Install rosdep dependencies
COPY --from=rosdep-base /rosdep-core-common-depend-packages.txt /tmp/rosdep-core-common-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-core-common-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/core/autoware_adapi_msgs,target=/autoware/src/core/autoware_adapi_msgs \
  --mount=type=bind,source=src/core/autoware_cmake,target=/autoware/src/core/autoware_cmake \
  --mount=type=bind,source=src/core/autoware_internal_msgs,target=/autoware/src/core/autoware_internal_msgs \
  --mount=type=bind,source=src/core/autoware_lanelet2_extension,target=/autoware/src/core/autoware_lanelet2_extension \
  --mount=type=bind,source=src/core/autoware_msgs,target=/autoware/src/core/autoware_msgs \
  --mount=type=bind,source=src/core/autoware_utils,target=/autoware/src/core/autoware_utils \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

# =============================================================================
# Stage: core-devel
# Builds core packages (extends core-common-devel)
# =============================================================================
FROM core-common-devel AS core-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-base /rosdep-core-depend-packages.txt /tmp/rosdep-core-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-core-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/core/autoware_core,target=/autoware/src/core/autoware_core \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Stage: universe-common-devel
# Builds common universe packages
# =============================================================================
FROM core-devel AS universe-common-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-base /rosdep-universe-common-depend-packages.txt /tmp/rosdep-universe-common-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-common-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/autoware_universe/common,target=/autoware/src/universe/autoware_universe/common \
  --mount=type=bind,source=src/universe/external/eagleye,target=/autoware/src/universe/external/eagleye \
  --mount=type=bind,source=src/universe/external/glog,target=/autoware/src/universe/external/glog \
  --mount=type=bind,source=src/universe/external/llh_converter,target=/autoware/src/universe/external/llh_converter \
  --mount=type=bind,source=src/universe/external/managed_transform_buffer,target=/autoware/src/universe/external/managed_transform_buffer \
  --mount=type=bind,source=src/universe/external/morai_msgs,target=/autoware/src/universe/external/morai_msgs \
  --mount=type=bind,source=src/universe/external/muSSP,target=/autoware/src/universe/external/muSSP \
  --mount=type=bind,source=src/universe/external/pointcloud_to_laserscan,target=/autoware/src/universe/external/pointcloud_to_laserscan \
  --mount=type=bind,source=src/universe/external/rtklib_ros_bridge,target=/autoware/src/universe/external/rtklib_ros_bridge \
  --mount=type=bind,source=src/universe/external/tier4_ad_api_adaptor,target=/autoware/src/universe/external/tier4_ad_api_adaptor \
  --mount=type=bind,source=src/universe/external/tier4_autoware_msgs,target=/autoware/src/universe/external/tier4_autoware_msgs \
  --mount=type=bind,source=src/middleware/external,target=/autoware/src/middleware/external \
  --mount=type=bind,source=src/launcher,target=/autoware/src/launcher \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Stage: universe-common-devel-cuda
# Universe-common with CUDA support
# =============================================================================
FROM universe-common-devel AS universe-common-devel-cuda
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO

# Set up CUDA development environment
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  ./setup-dev-env.sh -y --module all --no-cuda-drivers openadkit --ros-distro "$ROS_DISTRO" \
  && pipx uninstall ansible \
  && /autoware/cleanup_apt.sh true

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Stage: visualization-devel
# Builds visualization packages
# =============================================================================
FROM universe-common-devel AS visualization-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-base /rosdep-universe-visualization-depend-packages.txt /tmp/rosdep-universe-visualization-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-visualization-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/autoware_universe/visualization,target=/autoware/src/universe/autoware_universe/visualization \
  --mount=type=bind,source=src/core/autoware_rviz_plugins,target=/autoware/src/core/autoware_rviz_plugins \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Stage: universe-visualization
# Runtime image for visualization
# =============================================================================
FROM base AS universe-visualization
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-base /rosdep-universe-visualization-exec-depend-packages.txt /tmp/rosdep-universe-visualization-exec-depend-packages.txt
# hadolint ignore=SC2002
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-universe-visualization-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=visualization-devel /opt/autoware /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
