# Dockerfile.planning-control - Builds planning and control packages
# Outputs: universe-planning-control runtime image

ARG ROSDEP_IMAGE=ghcr.io/autowarefoundation/openadkit/rosdep-depend:latest
ARG UNIVERSE_COMMON_DEVEL_IMAGE=ghcr.io/autowarefoundation/openadkit/universe-common-devel:latest
ARG AUTOWARE_BASE_IMAGE=ghcr.io/autowarefoundation/autoware-base:latest
ARG ROS_DISTRO=humble
ARG LIB_DIR=x86_64

# Import rosdep dependency lists
# hadolint ignore=DL3006
FROM $ROSDEP_IMAGE AS rosdep-depend

# =============================================================================
# Build stage: planning-control-devel
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_IMAGE AS planning-control-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-planning-control-depend-packages.txt /tmp/rosdep-universe-planning-control-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-planning-control-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_control_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_control_launch \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_planning_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_planning_launch \
  --mount=type=bind,source=src/universe/autoware_universe/control,target=/autoware/src/universe/autoware_universe/control \
  --mount=type=bind,source=src/universe/autoware_universe/planning,target=/autoware/src/universe/autoware_universe/planning \
  # TODO(youtalk): Remove mounts when https://github.com/autowarefoundation/autoware_universe/issues/8805 is resolved
  --mount=type=bind,source=src/universe/autoware_universe/evaluator/autoware_control_evaluator,target=/autoware/src/universe/autoware_universe/evaluator/autoware_control_evaluator \
  --mount=type=bind,source=src/universe/autoware_universe/evaluator/autoware_planning_evaluator,target=/autoware/src/universe/autoware_universe/evaluator/autoware_planning_evaluator \
  --mount=type=bind,source=src/universe/autoware_universe/sensing/autoware_pcl_extensions,target=/autoware/src/universe/autoware_universe/sensing/autoware_pcl_extensions \
  --mount=type=bind,source=src/universe/autoware_universe/sensing/autoware_pointcloud_preprocessor,target=/autoware/src/universe/autoware_universe/sensing/autoware_pointcloud_preprocessor \
  --mount=type=bind,source=src/universe/autoware_universe/vehicle/autoware_external_cmd_converter,target=/autoware/src/universe/autoware_universe/vehicle/autoware_external_cmd_converter \
  --mount=type=bind,source=src/universe/autoware_universe/vehicle/autoware_raw_vehicle_cmd_converter,target=/autoware/src/universe/autoware_universe/vehicle/autoware_raw_vehicle_cmd_converter \
  --mount=type=bind,source=src/universe/autoware_universe/system/autoware_command_mode_types,target=/autoware/src/universe/autoware_universe/system/autoware_command_mode_types \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Runtime stage: universe-planning-control
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_IMAGE AS universe-planning-control
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-universe-planning-control-exec-depend-packages.txt /tmp/rosdep-universe-planning-control-exec-depend-packages.txt
# hadolint ignore=SC2002
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-universe-planning-control-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=planning-control-devel /opt/autoware /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
