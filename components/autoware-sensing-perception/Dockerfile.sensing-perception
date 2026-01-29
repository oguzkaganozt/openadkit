# Dockerfile.sensing-perception - Builds sensing and perception packages
# Outputs: universe-sensing-perception and universe-sensing-perception-cuda runtime images

ARG ROSDEP_IMAGE=ghcr.io/autowarefoundation/openadkit/rosdep-depend:latest
ARG UNIVERSE_COMMON_DEVEL_IMAGE=ghcr.io/autowarefoundation/openadkit/universe-common-devel:latest
ARG UNIVERSE_COMMON_DEVEL_CUDA_IMAGE=ghcr.io/autowarefoundation/openadkit/universe-common-devel-cuda:latest
ARG AUTOWARE_BASE_IMAGE=ghcr.io/autowarefoundation/autoware-base:latest
ARG AUTOWARE_BASE_CUDA_IMAGE=ghcr.io/autowarefoundation/autoware-base:cuda-latest
ARG ROS_DISTRO=humble
ARG LIB_DIR=x86_64

# Import rosdep dependency lists
# hadolint ignore=DL3006
FROM $ROSDEP_IMAGE AS rosdep-depend

# =============================================================================
# Build stage: sensing-perception-devel (non-CUDA)
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_IMAGE AS sensing-perception-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-sensing-perception-depend-packages.txt /tmp/rosdep-universe-sensing-perception-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-sensing-perception-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_perception_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_perception_launch \
  --mount=type=bind,source=src/universe/autoware_universe/launch/tier4_sensing_launch,target=/autoware/src/universe/autoware_universe/launch/tier4_sensing_launch \
  --mount=type=bind,source=src/universe/external/trt_batched_nms,target=/autoware/src/universe/external/trt_batched_nms \
  --mount=type=bind,source=src/universe/autoware_universe/perception,target=/autoware/src/universe/autoware_universe/perception \
  --mount=type=bind,source=src/universe/autoware_universe/sensing,target=/autoware/src/universe/autoware_universe/sensing \
  --mount=type=bind,source=src/universe/autoware_universe/evaluator/autoware_perception_online_evaluator,target=/autoware/src/universe/autoware_universe/evaluator/autoware_perception_online_evaluator \
  --mount=type=bind,source=src/sensor_component,target=/autoware/src/sensor_component \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

# =============================================================================
# Build stage: sensing-perception-devel-cuda
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_CUDA_IMAGE AS sensing-perception-devel-cuda
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-sensing-perception-depend-packages.txt /tmp/rosdep-universe-sensing-perception-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-sensing-perception-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

COPY --from=sensing-perception-devel /opt/autoware /opt/autoware

# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/universe/external/negotiated,target=/autoware/src/universe/external/negotiated \
  --mount=type=bind,source=src/universe/external/cuda_blackboard,target=/autoware/src/universe/external/cuda_blackboard \
  --mount=type=bind,source=src/universe/autoware_universe/perception,target=/autoware/src/universe/autoware_universe/perception \
  --mount=type=bind,source=src/universe/autoware_universe/sensing,target=/autoware/src/universe/autoware_universe/sensing \
  --mount=type=bind,source=src/universe/autoware_universe/common/autoware_cuda_dependency_meta,target=/autoware/src/universe/autoware_universe/common/autoware_cuda_dependency_meta \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware "--packages-above-and-dependencies autoware_cuda_dependency_meta"

# =============================================================================
# Runtime stage: universe-sensing-perception (non-CUDA)
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_IMAGE AS universe-sensing-perception
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-universe-sensing-perception-exec-depend-packages.txt /tmp/rosdep-universe-sensing-perception-exec-depend-packages.txt
# hadolint ignore=SC2002
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-universe-sensing-perception-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=sensing-perception-devel /opt/autoware /opt/autoware
# TODO(youtalk): Fix https://github.com/autowarefoundation/autoware/pull/6235 workaround
COPY --from=sensing-perception-devel /opt/autoware/share/autoware_launch /opt/autoware/share/autoware_launch

# Copy bash aliases
COPY docker/etc/.bash_aliases /root/.bash_aliases
RUN echo "source /opt/autoware/setup.bash" > /etc/bash.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Runtime stage: universe-sensing-perception-cuda
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_CUDA_IMAGE AS universe-sensing-perception-cuda
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-universe-sensing-perception-exec-depend-packages.txt /tmp/rosdep-universe-sensing-perception-exec-depend-packages.txt
# hadolint ignore=SC2002
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-universe-sensing-perception-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=sensing-perception-devel-cuda /opt/autoware /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
