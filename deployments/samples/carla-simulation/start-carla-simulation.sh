#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DRY_RUN=false
USE_GPU=true
VERIFY=true
PLANNING_DEMO=false

usage() {
  cat <<'EOF'
Usage: ./start-carla-simulation.sh [options]

Starts the CARLA simulation sample in a race-safe order:
  1. start CARLA
  2. wait for CARLA RPC
  3. recreate CARLA ROS bridge
  4. wait for bridge object spawning
  5. start the remaining OpenADKit services
  6. verify /clock and key topics

Options:
  --planning-demo Use dummy Autoware vehicle/perception and a bridge launch
                  that leaves RViz /initialpose for Autoware only
  --no-gpu        Do not include docker-compose.gpu.override.yaml
  --skip-verify   Skip ROS topic and /clock verification
  --dry-run       Print the planned commands without running them
  -h, --help      Show this help text
EOF
}

while (($#)); do
  case "$1" in
    --planning-demo)
      PLANNING_DEMO=true
      ;;
    --no-gpu)
      USE_GPU=false
      ;;
    --skip-verify)
      VERIFY=false
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

ENV_FILES=(carla-simulation.env)
if [[ "$PLANNING_DEMO" == true ]]; then
  ENV_FILES+=(carla-simulation.planning-demo.env)
fi

COMPOSE=(docker compose)
for env_file in "${ENV_FILES[@]}"; do
  COMPOSE+=(--env-file "$env_file")
done
COMPOSE+=(-f docker-compose.yaml)
if [[ "$USE_GPU" == true ]]; then
  COMPOSE+=(-f docker-compose.gpu.override.yaml)
fi
if [[ "$PLANNING_DEMO" == true ]]; then
  COMPOSE+=(-f docker-compose.planning-demo.override.yaml)
fi

compose_text() {
  local parts=()
  local arg
  for arg in "${COMPOSE[@]}" "$@"; do
    parts+=("$arg")
  done
  printf '%s' "${parts[*]}"
}

run_compose() {
  local text
  text=$(compose_text "$@")
  printf '+ %s\n' "$text"
  if [[ "$DRY_RUN" == false ]]; then
    "${COMPOSE[@]}" "$@"
  fi
}

load_env_defaults() {
  local env_keys=()
  local line
  local env_file
  for env_file in "${ENV_FILES[@]}"; do
    while IFS= read -r line; do
      if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)= ]]; then
        env_keys+=("${BASH_REMATCH[1]}")
      fi
    done < "$env_file"
  done

  local overrides=()
  local key
  for key in "${env_keys[@]}"; do
    if [[ ${!key+x} ]]; then
      overrides+=("$key=${!key}")
    fi
  done

  set -a
  for env_file in "${ENV_FILES[@]}"; do
    # shellcheck source=/dev/null
    source "$env_file"
  done
  set +a

  local override
  for override in "${overrides[@]}"; do
    export "$override"
  done
}

wait_for_carla_rpc() {
  printf '+ wait for CARLA RPC on %s:%s\n' "$CARLA_RPC_HOST" "$CARLA_RPC_PORT"
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  local deadline=$((SECONDS + CARLA_RPC_TIMEOUT))
  while ((SECONDS < deadline)); do
    if timeout 1 bash -c "</dev/tcp/${CARLA_RPC_HOST}/${CARLA_RPC_PORT}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 5
  done

  docker logs --tail 120 carla >&2 || true
  printf 'Timed out waiting for CARLA RPC on %s:%s\n' "$CARLA_RPC_HOST" "$CARLA_RPC_PORT" >&2
  return 1
}

wait_for_bridge_spawn() {
  printf '+ wait for bridge log: All objects spawned.\n'
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  local deadline=$((SECONDS + BRIDGE_TIMEOUT))
  local logs
  while ((SECONDS < deadline)); do
    logs=$(docker logs carla-ros-bridge 2>&1 || true)
    case "$logs" in
      *"All objects spawned."*)
        return 0
        ;;
      *"ModuleNotFoundError"*|*"process has died"*)
        docker logs --tail 160 carla-ros-bridge >&2 || true
        return 1
        ;;
    esac
    sleep 5
  done

  docker logs --tail 200 carla-ros-bridge >&2 || true
  printf 'Timed out waiting for CARLA bridge object spawning\n' >&2
  return 1
}

verify_runtime() {
  if [[ "$VERIFY" == false ]]; then
    return 0
  fi

  printf '+ verify /clock and key topics\n'
  if [[ "$DRY_RUN" == true ]]; then
    return 0
  fi

  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
  docker inspect -f '{{.Name}} restart={{.RestartCount}} state={{.State.Status}}' carla carla-ros-bridge

  local required_topics=(
    /clock
    /carla/status
    /carla/ego_vehicle/lidar
    /carla/ego_vehicle/rgb_front/image
    /planning/trajectory
    /control/command/control_cmd
    /vehicle/status/velocity_status
  )
  local missing_topics=()
  local topics=''
  local clock_output=''
  local topic
  local deadline=$((SECONDS + RUNTIME_VERIFY_TIMEOUT))

  while :; do
    missing_topics=()

    if ! clock_output=$(docker exec autoware-map bash -lc \
      'source /opt/ros/humble/setup.bash && timeout 10 ros2 topic echo --once /clock' 2>&1); then
      missing_topics+=(/clock)
    fi

    if topics=$(docker exec autoware-map bash -lc \
      'source /opt/ros/humble/setup.bash && timeout 10 ros2 topic list' 2>&1); then
      for topic in "${required_topics[@]}"; do
        if [[ $'\n'"$topics"$'\n' != *$'\n'"$topic"$'\n'* ]]; then
          missing_topics+=("$topic")
        fi
      done
    else
      missing_topics+=("ros2 topic list")
    fi

    if ((${#missing_topics[@]} == 0)); then
      printf '%s\n' "$clock_output"
      printf '%s\n' "$topics"
      return 0
    fi

    if ((SECONDS >= deadline)); then
      break
    fi

    sleep "$RUNTIME_VERIFY_INTERVAL"
  done

  printf 'Timed out waiting for runtime verification. Missing expected topics:\n' >&2
  printf '  %s\n' "${missing_topics[@]}" >&2
  if [[ -n "$topics" ]]; then
    printf 'Last topic list:\n%s\n' "$topics" >&2
  fi
  return 1
}

main() {
  cd "$SCRIPT_DIR"

  load_env_defaults
  : "${CARLA_RPC_HOST:=127.0.0.1}"
  : "${CARLA_RPC_PORT:=2000}"
  : "${CARLA_RPC_TIMEOUT:=600}"
  : "${BRIDGE_TIMEOUT:=600}"
  : "${RUNTIME_VERIFY_TIMEOUT:=120}"
  : "${RUNTIME_VERIFY_INTERVAL:=5}"

  if [[ "$DRY_RUN" == false && ! -d "${MAP_PATH:-$HOME/autoware_map/sample-map-planning}" ]]; then
    printf 'Map path not found: %s\n' "${MAP_PATH:-$HOME/autoware_map/sample-map-planning}" >&2
    printf 'Download the planning map or set MAP_PATH before starting.\n' >&2
    return 1
  fi

  run_compose up -d carla
  wait_for_carla_rpc
  run_compose up -d --force-recreate --no-deps carla-ros-bridge
  wait_for_bridge_spawn
  run_compose up -d
  verify_runtime
}

main
