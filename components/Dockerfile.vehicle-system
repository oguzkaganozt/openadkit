# Dockerfile.vehicle-system - Builds vehicle and system packages
# Outputs: universe-vehicle-system runtime image

ARG ROSDEP_IMAGE=ghcr.io/autowarefoundation/openadkit/rosdep-depend:latest
ARG UNIVERSE_COMMON_DEVEL_IMAGE=ghcr.io/autowarefoundation/openadkit/universe-common-devel:latest
ARG AUTOWARE_BASE_IMAGE=ghcr.io/autowarefoundation/autoware-base:latest
ARG ROS_DISTRO=humble
ARG LIB_DIR=x86_64

# Import rosdep dependency lists
# hadolint ignore=DL3006
FROM $ROSDEP_IMAGE AS rosdep-depend

# =============================================================================
# Build stage: vehicle-system-devel
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_IMAGE AS vehicle-system-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-vehicle-system-depend-packages.txt /tmp/rosdep-universe-vehicle-system-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-vehicle-system-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_vehicle_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_vehicle_launch \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_system_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_system_launch \
  --mount=type=bind,source=src/universe/autoware_universe/vehicle,target=/autoware/src/universe/autoware_universe/vehicle \
  --mount=type=bind,source=src/universe/autoware_universe/system,target=/autoware/src/universe/autoware_universe/system \
  --mount=type=bind,source=src/core/autoware_core/map/autoware_map_height_fitter,target=/autoware/src/core/autoware_core/map/autoware_map_height_fitter \
  --mount=type=bind,source=src/universe/autoware_universe/localization/autoware_pose2twist,target=/autoware/src/universe/autoware_universe/localization/autoware_pose2twist \
  --mount=type=bind,source=src/universe/autoware_universe/planning/planning_validator,target=/autoware/src/universe/autoware_universe/planning/planning_validator \
  --mount=type=bind,source=src/sensor_component/external/sensor_component_description,target=/autoware/src/sensor_component/external/sensor_component_description \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Runtime stage: universe-vehicle-system
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_IMAGE AS universe-vehicle-system
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-universe-vehicle-system-exec-depend-packages.txt /tmp/rosdep-universe-vehicle-system-exec-depend-packages.txt
# hadolint ignore=SC2002
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-universe-vehicle-system-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=vehicle-system-devel /opt/autoware /opt/autoware

# Copy bash aliases
COPY docker/etc/.bash_aliases /root/.bash_aliases
RUN echo "source /opt/autoware/setup.bash" > /etc/bash.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
