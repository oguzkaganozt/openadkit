# autoware-universe/Dockerfile - Combines all component packages into a single image
# Outputs: universe and universe-cuda runtime images

ARG ROSDEP_IMAGE=ghcr.io/autowarefoundation/openadkit/rosdep-depend:latest
ARG AUTOWARE_COMMON_DEVEL_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-common-devel:latest
ARG AUTOWARE_COMMON_DEVEL_CUDA_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-common-devel-cuda:latest
ARG AUTOWARE_SENSING_PERCEPTION_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-sensing-perception:latest
ARG AUTOWARE_SENSING_PERCEPTION_CUDA_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-sensing-perception-cuda:latest
ARG AUTOWARE_LOCALIZATION_MAPPING_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-localization-mapping:latest
ARG AUTOWARE_PLANNING_CONTROL_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-planning-control:latest
ARG AUTOWARE_VEHICLE_SYSTEM_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-vehicle-system:latest
ARG AUTOWARE_VISUALIZATION_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-visualization:latest
ARG AUTOWARE_API_IMAGE=ghcr.io/autowarefoundation/openadkit/autoware-api:latest
ARG AUTOWARE_BASE_IMAGE=ghcr.io/autowarefoundation/autoware-base:latest
ARG AUTOWARE_BASE_CUDA_IMAGE=ghcr.io/autowarefoundation/autoware-base:cuda-latest
ARG ROS_DISTRO=humble
ARG LIB_DIR=x86_64

# Import rosdep dependency lists
# hadolint ignore=DL3006
FROM $ROSDEP_IMAGE AS rosdep-depend

# Import component images for COPY
# hadolint ignore=DL3006
FROM $SENSING_PERCEPTION_IMAGE AS sensing-perception
# hadolint ignore=DL3006
FROM $SENSING_PERCEPTION_CUDA_IMAGE AS sensing-perception-cuda
# hadolint ignore=DL3006
FROM $LOCALIZATION_MAPPING_IMAGE AS localization-mapping
# hadolint ignore=DL3006
FROM $PLANNING_CONTROL_IMAGE AS planning-control
# hadolint ignore=DL3006
FROM $VEHICLE_SYSTEM_IMAGE AS vehicle-system
# hadolint ignore=DL3006
FROM $VISUALIZATION_IMAGE AS visualization
# hadolint ignore=DL3006
FROM $API_IMAGE AS api

# =============================================================================
# Build stage: universe-devel (combines all components)
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_IMAGE AS universe-devel
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ENV CCACHE_DIR="/root/.ccache"

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-depend-packages.txt /tmp/rosdep-universe-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# Copy compiled artifacts from all component images
COPY --from=sensing-perception /opt/autoware /opt/autoware
COPY --from=localization-mapping /opt/autoware /opt/autoware
COPY --from=planning-control /opt/autoware /opt/autoware
COPY --from=vehicle-system /opt/autoware /opt/autoware
COPY --from=visualization /opt/autoware /opt/autoware
COPY --from=api /opt/autoware /opt/autoware

# Strip unneeded symbols from binaries in /opt/autoware
RUN find /opt/autoware -type f \( -executable -o -name "*.so" \) -exec strip --strip-unneeded --remove-section=.comment --remove-section=.note {} \;

# Build remaining packages (evaluators, simulators, tools, etc.)
# hadolint ignore=SC1091
RUN --mount=type=cache,target="${CCACHE_DIR}" \
  --mount=type=bind,source=src/sensor_component,target=/autoware/src/sensor_component \
  --mount=type=bind,source=src/universe/autoware_universe/evaluator,target=/autoware/src/universe/autoware_universe/evaluator \
  --mount=type=bind,source=src/universe/autoware_universe/launch,target=/autoware/src/universe/autoware_universe/launch \
  --mount=type=bind,source=src/universe/autoware_universe/simulator,target=/autoware/src/universe/autoware_universe/simulator \
  --mount=type=bind,source=src/universe/autoware_universe/tools,target=/autoware/src/universe/autoware_universe/tools \
  source /opt/ros/"$ROS_DISTRO"/setup.bash \
  && source /opt/autoware/setup.bash \
  && /autoware/build_and_clean.sh "${CCACHE_DIR}" /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Build stage: universe-devel-cuda
# =============================================================================
# hadolint ignore=DL3006
FROM $UNIVERSE_COMMON_DEVEL_CUDA_IMAGE AS universe-devel-cuda
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install rosdep dependencies
COPY --from=rosdep-depend /rosdep-universe-depend-packages.txt /tmp/rosdep-universe-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  apt-get update \
  && cat /tmp/rosdep-universe-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_apt.sh

# Copy from universe-devel and add CUDA-specific packages
COPY --from=universe-devel /opt/autoware /opt/autoware
COPY --from=sensing-perception-cuda /opt/autoware /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Runtime stage: universe (non-CUDA)
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_IMAGE AS universe
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-exec-depend-packages.txt /tmp/rosdep-exec-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=universe-devel /opt/autoware /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]

# =============================================================================
# Runtime stage: universe-cuda
# =============================================================================
# hadolint ignore=DL3006
FROM $AUTOWARE_BASE_CUDA_IMAGE AS universe-cuda
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG ROS_DISTRO
ARG LIB_DIR

# Set up runtime environment
COPY --from=rosdep-depend /rosdep-exec-depend-packages.txt /tmp/rosdep-exec-depend-packages.txt
# hadolint ignore=SC2002,DL3009
RUN --mount=type=ssh \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  ./setup-dev-env.sh -y --module all --no-nvidia --no-cuda-drivers --runtime openadkit --ros-distro $ROS_DISTRO \
  && pipx uninstall ansible \
  && apt-get update \
  && cat /tmp/rosdep-exec-depend-packages.txt | xargs apt-get install -y --no-install-recommends \
  && /autoware/cleanup_system.sh $LIB_DIR $ROS_DISTRO

COPY --from=universe-devel-cuda /opt/autoware /opt/autoware

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["/bin/bash"]
