# Dockerfile.localization-mapping - Builds localization and mapping packages
# Outputs: universe-localization-mapping runtime image

ARG ROSDEP_IMAGE=ghcr.io/autowarefoundation/openadkit/rosdep-depend:latest
ARG UNIVERSE_COMMON_DEVEL_IMAGE=ghcr.io/autowarefoundation/openadkit/universe-common-devel:latest
ARG AUTOWARE_BASE_IMAGE=ghcr.io/autowarefoundation/autoware-base:latest
ARG ROS_DISTRO=humble
ARG LIB_DIR=x86_64

# Import rosdep dependency lists
# hadolint ignore=DL3006
FROM $ROSDEP_IMAGE AS rosdep-depend

# =============================================================================
# Build stage: localization-mapping-devel
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_IMAGE AS localization-mapping-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-localization-mapping-depend-packages.txt /tmp/rosdep-universe-localization-mapping-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-localization-mapping-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_localization_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_localization_launch \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_map_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_map_launch \
  --mount=type=bind,source=src/universe/autoware_universe/localization,target=/autoware/src/universe/autoware_universe/localization \
  --mount=type=bind,source=src/universe/autoware_universe/map,target=/autoware/src/universe/autoware_universe/map \
  # TODO(youtalk): Remove mounts when https://github.com/autowarefoundation/autoware_universe/issues/10282 is resolved
  --mount=type=bind,source=src/universe/autoware_universe/sensing/autoware_pcl_extensions,target=/autoware/src/universe/autoware_universe/sensing/autoware_pcl_extensions \
  --mount=type=bind,source=src/universe/autoware_universe/sensing/autoware_pointcloud_preprocessor,target=/autoware/src/universe/autoware_universe/sensing/autoware_pointcloud_preprocessor \
  --mount=type=bind,source=src/universe/autoware_universe/system/autoware_default_adapi_helpers/autoware_automatic_pose_initializer,target=/autoware/src/universe/autoware_universe/system/autoware_default_adapi_helpers/autoware_automatic_pose_initializer \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

# =============================================================================
# Runtime stage: universe-localization-mapping
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_IMAGE AS universe-localization-mapping
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-universe-localization-mapping-exec-depend-packages.txt /tmp/rosdep-universe-localization-mapping-exec-depend-packages.txt
# hadolint ignore=SC2002
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-universe-localization-mapping-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=localization-mapping-devel /opt/autoware /opt/autoware

# Copy bash aliases
COPY docker/etc/.bash_aliases /root/.bash_aliases
RUN echo "source /opt/autoware/setup.bash" > /etc/bash.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
