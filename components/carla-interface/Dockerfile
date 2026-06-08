ARG SIMULATOR_IMAGE=ghcr.io/autowarefoundation/openadkit:simulator
FROM ${SIMULATOR_IMAGE} AS carla-interface

ARG CARLA_PYTHON_VERSION=0.9.16

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ros-humble-compressed-image-transport \
    ros-humble-topic-tools \
  && python3 -m pip install --no-cache-dir \
    carla==${CARLA_PYTHON_VERSION} \
    transforms3d \
  && rm -rf /var/lib/apt/lists/*

# TODO: Remove this patch once autowarefoundation/autoware_universe#12616
# is merged and available in the base simulator image.
# CARLA can crash when the interface reloads the same visible map during
# startup. Preload Town01 in the launcher, then use CARLA's conditional
# world loader while preserving map reloads for other maps.
RUN python3 - <<'PY'
import autoware_carla_interface
from pathlib import Path

path = Path(autoware_carla_interface.__file__).parent / "carla_autoware.py"
text = path.read_text()
old = '        client.load_world(self.carla_map)\n'
new = '        client.load_world_if_different(self.carla_map)\n'
if old in text:
    path.write_text(text.replace(old, new, 1))
elif new not in text:
    raise SystemExit('autoware_carla_interface load_world call not found')
PY
