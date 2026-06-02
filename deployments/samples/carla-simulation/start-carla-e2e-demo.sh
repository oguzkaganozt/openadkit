#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../../.." && pwd)
ENV_FILE=carla-simulation.e2e.env
DRY_RUN=false
BUILD_IMAGE=false
SKIP_VERIFY=false
START_VISUALIZER_OVERRIDE=
AUTO_DRIVE_OVERRIDE=

usage() {
  cat <<'EOF'
Usage: ./start-carla-e2e-demo.sh [options]

Starts the closed-loop CARLA e2e demo using CARLA on the host display and
Autoware's in-tree autoware_carla_interface.

Options:
  --build               Build the local CARLA interface image from tools
  --skip-build          Do not build the local CARLA interface image (default)
  --skip-verify         Skip topic, actor, and localization verification
  --no-visualizer       Do not start the browser RViz/noVNC visualizer container
  --drive               Set a forward route and engage autonomous mode
  --no-drive            Start the stack without setting a route or engaging
  --dry-run             Print planned commands without running them
  -h, --help            Show this help text
EOF
}

while (($#)); do
  case "$1" in
    --build)
      BUILD_IMAGE=true
      ;;
    --skip-build)
      BUILD_IMAGE=false
      ;;
    --skip-verify)
      SKIP_VERIFY=true
      ;;
    --no-visualizer)
      START_VISUALIZER_OVERRIDE=false
      ;;
    --drive)
      AUTO_DRIVE_OVERRIDE=true
      ;;
    --no-drive)
      AUTO_DRIVE_OVERRIDE=false
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

run() {
  printf '+ %s\n' "$*"
  if [[ "$DRY_RUN" == false ]]; then
    "$@"
  fi
}

run_compose() {
  printf '+ docker compose --env-file %s -f docker-compose.yaml %s\n' "$ENV_FILE" "$*"
  if [[ "$DRY_RUN" == false ]]; then
    docker compose --env-file "$ENV_FILE" -f docker-compose.yaml "$@"
  fi
}

load_env() {
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a

  if [[ -n "$START_VISUALIZER_OVERRIDE" ]]; then
    AUTOWARE_E2E_START_VISUALIZER=$START_VISUALIZER_OVERRIDE
  fi

  if [[ -n "$AUTO_DRIVE_OVERRIDE" ]]; then
    AUTOWARE_E2E_AUTO_DRIVE=$AUTO_DRIVE_OVERRIDE
  fi
}

prepare_map() {
  if [[ "$DRY_RUN" == true ]]; then
    printf '+ prepare CARLA Town01 map at %s\n' "$CARLA_E2E_MAP_PATH"
    return 0
  fi

  mkdir -p "$CARLA_E2E_MAP_PATH"

  if [[ ! -s "$CARLA_E2E_MAP_PATH/pointcloud_map.pcd" ]]; then
    run curl -L --fail -A Mozilla/5.0 -o "$CARLA_E2E_MAP_PATH/pointcloud_map.pcd" "$CARLA_E2E_POINTCLOUD_URL"
  fi

  if [[ ! -s "$CARLA_E2E_MAP_PATH/lanelet2_map.osm" ]]; then
    run curl -L --fail -A Mozilla/5.0 -o "$CARLA_E2E_MAP_PATH/lanelet2_map.osm" "$CARLA_E2E_LANELET2_URL"
  fi

  printf 'projector_type: Local\n' > "$CARLA_E2E_MAP_PATH/map_projector_info.yaml"
}

build_image() {
  if [[ "$BUILD_IMAGE" != true ]]; then
    return 0
  fi

  run docker buildx bake \
    --load \
    --progress=plain \
    -f "$REPO_ROOT/tools/docker-bake.hcl" \
    --set "*.context=$REPO_ROOT" \
    --set "carla-interface.tags=$CARLA_INTERFACE_IMAGE" \
    --set "carla-interface.args.CARLA_PYTHON_VERSION=$CARLA_PYTHON_VERSION" \
    carla-interface
}

wait_for_carla_rpc() {
  printf '+ wait for CARLA RPC on %s:%s\n' "$CARLA_RPC_HOST" "$CARLA_RPC_PORT"
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  local deadline=$((SECONDS + CARLA_START_TIMEOUT))
  while ((SECONDS < deadline)); do
    if timeout 1 bash -c "</dev/tcp/${CARLA_RPC_HOST}/${CARLA_RPC_PORT}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done

  printf 'Timed out waiting for CARLA RPC on %s:%s\n' "$CARLA_RPC_HOST" "$CARLA_RPC_PORT" >&2
  return 1
}

wait_for_carla_api() {
  printf '+ wait for CARLA Python API on %s:%s\n' "$CARLA_RPC_HOST" "$CARLA_RPC_PORT"
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  local deadline=$((SECONDS + CARLA_START_TIMEOUT))
  while ((SECONDS < deadline)); do
    if docker run --rm --network host "$CARLA_INTERFACE_IMAGE" bash -lc "python3 - <<'PY'
import carla
client = carla.Client('$CARLA_RPC_HOST', int('$CARLA_RPC_PORT'))
client.set_timeout(5)
print(client.get_world().get_map().name)
PY" >/dev/null 2>&1; then
      return 0
    fi
    sleep 5
  done

  printf 'Timed out waiting for CARLA Python API on %s:%s\n' "$CARLA_RPC_HOST" "$CARLA_RPC_PORT" >&2
  return 1
}

stop_container_carla() {
  run docker rm -f "$CARLA_CONTAINER_NAME" || true
}

start_container_carla() {
  if [[ "$DRY_RUN" == false && ! -S /tmp/.X11-unix/X${CARLA_DISPLAY#:} ]]; then
    printf 'X display socket for %s was not found under /tmp/.X11-unix\n' "$CARLA_DISPLAY" >&2
    return 1
  fi

  stop_container_carla
  run_compose up -d --force-recreate carla

  wait_for_carla_rpc
  wait_for_carla_api
}

preload_carla_world() {
  if [[ "$DRY_RUN" == true ]]; then
    run docker run --rm --network host "$CARLA_INTERFACE_IMAGE" bash -lc "python3 - <<'PY'
import carla
client = carla.Client('$CARLA_RPC_HOST', int('$CARLA_RPC_PORT'))
client.set_timeout(float('$CARLA_LOAD_TIMEOUT'))
world = client.load_world('$CARLA_WORLD')
print(world.get_map().name)
PY"
    return 0
  fi

  local deadline=$((SECONDS + CARLA_LOAD_TIMEOUT))
  while ((SECONDS < deadline)); do
    if docker run --rm --network host "$CARLA_INTERFACE_IMAGE" bash -lc "python3 - <<'PY'
import carla
client = carla.Client('$CARLA_RPC_HOST', int('$CARLA_RPC_PORT'))
client.set_timeout(30)
world = client.load_world('$CARLA_WORLD')
print(world.get_map().name)
PY"; then
      return 0
    fi
    sleep 5
  done

  printf 'Timed out preloading CARLA world %s\n' "$CARLA_WORLD" >&2
  return 1
}

start_autoware() {
  run docker rm -f "$CARLA_INTERFACE_CONTAINER" || true
  if docker container inspect autoware-e2e-carla >/dev/null 2>&1; then
    run docker rm -f autoware-e2e-carla
  fi
  run_compose up -d --force-recreate \
    map \
    system \
    carla-interface \
    sensing \
    perception \
    localization \
    planning \
    vehicle \
    control \
    api
}

start_visualizer() {
  if [[ "$AUTOWARE_E2E_START_VISUALIZER" != true ]]; then
    return 0
  fi

  run docker rm -f autoware-e2e-visualizer || true
  run_compose up -d --force-recreate visualizer
}

verify_runtime() {
  if [[ "$SKIP_VERIFY" == true ]]; then
    return 0
  fi

  printf '+ verify CARLA e2e runtime\n'
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  local deadline=$((SECONDS + AUTOWARE_E2E_VERIFY_TIMEOUT))
  local output
  while ((SECONDS < deadline)); do
    if output=$(docker exec "$CARLA_INTERFACE_CONTAINER" bash -lc "source /opt/ros/humble/setup.bash; source /opt/autoware/setup.bash; python3 - <<'PY'
import time

import carla
import rclpy
from nav_msgs.msg import Odometry
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2

rclpy.init()
node = rclpy.create_node('openadkit_e2e_runtime_verifier')
latest_odom = None
latest_lidar = None

def on_odom(msg):
    global latest_odom
    latest_odom = msg

def on_lidar(msg):
    global latest_lidar
    latest_lidar = msg

node.create_subscription(Odometry, '/localization/kinematic_state', on_odom, 10)
node.create_subscription(PointCloud2, '/sensing/lidar/top/pointcloud_before_sync', on_lidar, qos_profile_sensor_data)

deadline = time.time() + 20.0
while time.time() < deadline and (latest_odom is None or latest_lidar is None):
    rclpy.spin_once(node, timeout_sec=0.2)

if latest_odom is None:
    raise RuntimeError('Timed out waiting for /localization/kinematic_state')
if latest_lidar is None:
    raise RuntimeError('Timed out waiting for /sensing/lidar/top/pointcloud_before_sync')

client = carla.Client('$CARLA_RPC_HOST', int('$CARLA_RPC_PORT'))
client.set_timeout(10)
world = client.get_world()
world.tick(2)
vehicles = [a for a in world.get_actors() if a.type_id.startswith('vehicle.')]
ego = [v for v in vehicles if v.attributes.get('role_name') == 'ego_vehicle']
print(world.get_map().name)
print('vehicles', len(vehicles), 'ego', len(ego))
if not ego:
    raise SystemExit(1)
node.destroy_node()
rclpy.shutdown()
PY" 2>&1); then
      printf '%s\n' "$output"
      return 0
    fi
    sleep "$AUTOWARE_E2E_VERIFY_INTERVAL"
  done

  docker compose --env-file "$ENV_FILE" -f docker-compose.yaml logs --tail 160 >&2 || true
  printf 'Timed out waiting for CARLA e2e verification\n' >&2
  return 1
}

start_autonomous_drive() {
  if [[ "$AUTOWARE_E2E_AUTO_DRIVE" != true ]]; then
    return 0
  fi

  printf '+ set forward route and engage autonomous mode\n'
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  docker exec \
    -e AUTOWARE_E2E_ROUTE_FORWARD_DISTANCE="$AUTOWARE_E2E_ROUTE_FORWARD_DISTANCE" \
    -e AUTOWARE_E2E_ROUTE_SETTLE_TIMEOUT="$AUTOWARE_E2E_ROUTE_SETTLE_TIMEOUT" \
    "$CARLA_INTERFACE_CONTAINER" \
    bash -lc "source /opt/ros/humble/setup.bash; source /opt/autoware/setup.bash; python3 - <<'PY'
import os
import time

import rclpy
from autoware_adapi_v1_msgs.msg import OperationModeState, RouteState
from autoware_adapi_v1_msgs.srv import ChangeOperationMode, ClearRoute, SetRoutePoints
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry

forward_distance = float(os.environ['AUTOWARE_E2E_ROUTE_FORWARD_DISTANCE'])
settle_timeout = float(os.environ['AUTOWARE_E2E_ROUTE_SETTLE_TIMEOUT'])
autonomous_mode = getattr(OperationModeState, 'AUTONOMOUS', 2)

rclpy.init()
node = rclpy.create_node('openadkit_e2e_route_and_engage')
latest_odom = None
latest_operation = None
latest_route = None

def on_odom(msg):
    global latest_odom
    latest_odom = msg

def on_operation(msg):
    global latest_operation
    latest_operation = msg

def on_route(msg):
    global latest_route
    latest_route = msg

node.create_subscription(Odometry, '/localization/kinematic_state', on_odom, 10)
node.create_subscription(OperationModeState, '/api/operation_mode/state', on_operation, 10)
node.create_subscription(RouteState, '/api/routing/state', on_route, 10)

def spin_until(predicate, timeout, description):
    deadline = time.time() + timeout
    while time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
        if predicate():
            return True
    raise RuntimeError(f'Timed out waiting for {description}')

def wait_for_service(client, timeout, name):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if client.wait_for_service(timeout_sec=1.0):
            return
    raise RuntimeError(f'Timed out waiting for service {name}')

def call_service(client, request, timeout, name):
    wait_for_service(client, timeout, name)
    future = client.call_async(request)
    deadline = time.time() + timeout
    while time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
        if future.done():
            response = future.result()
            if response is None:
                raise RuntimeError(f'{name} returned no response')
            status = getattr(response, 'status', None)
            if status is not None and not status.success:
                raise RuntimeError(f'{name} failed: {status.message}')
            return response
    raise RuntimeError(f'Timed out waiting for response from {name}')

spin_until(lambda: latest_odom is not None, settle_timeout, '/localization/kinematic_state')
start_pose = latest_odom.pose.pose

clear_route = node.create_client(ClearRoute, '/api/routing/clear_route')
set_route = node.create_client(SetRoutePoints, '/api/routing/set_route_points')
change_route = node.create_client(SetRoutePoints, '/api/routing/change_route_points')
change_to_autonomous = node.create_client(ChangeOperationMode, '/api/operation_mode/change_to_autonomous')

call_service(clear_route, ClearRoute.Request(), settle_timeout, '/api/routing/clear_route')

clear_deadline = time.time() + min(10.0, settle_timeout)
while time.time() < clear_deadline:
    rclpy.spin_once(node, timeout_sec=0.2)
    if latest_route is not None and latest_route.state == RouteState.UNSET:
        break

request = SetRoutePoints.Request()
request.header.frame_id = 'map'
request.option.allow_goal_modification = True
request.goal = Pose()
request.goal.position.x = start_pose.position.x + forward_distance
request.goal.position.y = start_pose.position.y
request.goal.position.z = 0.0
request.goal.orientation = start_pose.orientation

try:
    call_service(set_route, request, settle_timeout, '/api/routing/set_route_points')
except RuntimeError as error:
    if 'route is already set' not in str(error).lower() and 'invalid_state' not in str(error).lower():
        raise
    call_service(change_route, request, settle_timeout, '/api/routing/change_route_points')
print(
    'Route set: '
    f'start=({start_pose.position.x:.2f}, {start_pose.position.y:.2f}) '
    f'goal=({request.goal.position.x:.2f}, {request.goal.position.y:.2f})'
)

spin_until(
    lambda: latest_operation is not None and latest_operation.is_autonomous_mode_available,
    settle_timeout,
    'autonomous mode availability',
)
call_service(change_to_autonomous, ChangeOperationMode.Request(), settle_timeout, '/api/operation_mode/change_to_autonomous')
spin_until(
    lambda: latest_operation is not None and latest_operation.mode == autonomous_mode,
    settle_timeout,
    'autonomous mode transition',
)
print('Autonomous mode active')
node.destroy_node()
rclpy.shutdown()
PY"
}

verify_autonomous_drive() {
  if [[ "$AUTOWARE_E2E_AUTO_DRIVE" != true || "$SKIP_VERIFY" == true ]]; then
    return 0
  fi

  printf '+ verify autonomous CARLA motion\n'
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  docker exec \
    -e AUTOWARE_E2E_DRIVE_VERIFY_TIMEOUT="$AUTOWARE_E2E_DRIVE_VERIFY_TIMEOUT" \
    -e AUTOWARE_E2E_DRIVE_VERIFY_DISTANCE="$AUTOWARE_E2E_DRIVE_VERIFY_DISTANCE" \
    "$CARLA_INTERFACE_CONTAINER" \
    bash -lc "source /opt/ros/humble/setup.bash; source /opt/autoware/setup.bash; python3 - <<'PY'
import math
import os
import time

import rclpy
from nav_msgs.msg import Odometry

timeout = float(os.environ['AUTOWARE_E2E_DRIVE_VERIFY_TIMEOUT'])
required_distance = float(os.environ['AUTOWARE_E2E_DRIVE_VERIFY_DISTANCE'])

rclpy.init()
node = rclpy.create_node('openadkit_e2e_motion_verifier')
latest_odom = None

def on_odom(msg):
    global latest_odom
    latest_odom = msg

node.create_subscription(Odometry, '/localization/kinematic_state', on_odom, 10)

deadline = time.time() + timeout
while latest_odom is None and time.time() < deadline:
    rclpy.spin_once(node, timeout_sec=0.2)

if latest_odom is None:
    raise RuntimeError('Timed out waiting for /localization/kinematic_state')

start = latest_odom.pose.pose.position
start_x = start.x
start_y = start.y

while time.time() < deadline:
    rclpy.spin_once(node, timeout_sec=0.2)
    current = latest_odom.pose.pose.position
    distance = math.hypot(current.x - start_x, current.y - start_y)
    if distance >= required_distance:
        print(
            f'Moved {distance:.2f} m: '
            f'start=({start_x:.2f}, {start_y:.2f}) '
            f'current=({current.x:.2f}, {current.y:.2f})'
        )
        node.destroy_node()
        rclpy.shutdown()
        raise SystemExit(0)

current = latest_odom.pose.pose.position
distance = math.hypot(current.x - start_x, current.y - start_y)
raise RuntimeError(f'Autonomous motion verification failed: moved {distance:.2f} m')
PY"
}

main() {
  cd "$SCRIPT_DIR"
  load_env
  prepare_map
  build_image
  start_container_carla
  preload_carla_world
  start_autoware
  start_visualizer
  verify_runtime
  start_autonomous_drive
  verify_autonomous_drive
}

main
