#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SCRIPT="$SCRIPT_DIR/start-carla-simulation.sh"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

assert_contains() {
  local haystack=$1
  local needle=$2
  case "$haystack" in
    *"$needle"*) ;;
    *) fail "expected output to contain: $needle" ;;
  esac
}

assert_not_contains() {
  local haystack=$1
  local needle=$2
  case "$haystack" in
    *"$needle"*) fail "expected output not to contain: $needle" ;;
    *) ;;
  esac
}

help_output=$("$SCRIPT" --help)
assert_contains "$help_output" "Usage:"
assert_contains "$help_output" "--planning-demo"
assert_contains "$help_output" "--no-gpu"
assert_contains "$help_output" "--skip-verify"

gpu_plan=$("$SCRIPT" --dry-run)
assert_contains "$gpu_plan" "docker compose --env-file carla-simulation.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml up -d carla"
assert_contains "$gpu_plan" "docker compose --env-file carla-simulation.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml up -d --force-recreate --no-deps carla-ros-bridge"
assert_contains "$gpu_plan" "wait for CARLA RPC on 127.0.0.1:2000"
assert_contains "$gpu_plan" "wait for bridge log: All objects spawned."
assert_contains "$gpu_plan" "verify /clock and key topics"

no_gpu_plan=$("$SCRIPT" --dry-run --no-gpu --skip-verify)
assert_contains "$no_gpu_plan" "docker compose --env-file carla-simulation.env -f docker-compose.yaml up -d carla"
assert_contains "$no_gpu_plan" "docker compose --env-file carla-simulation.env -f docker-compose.yaml up -d --force-recreate --no-deps carla-ros-bridge"
assert_not_contains "$no_gpu_plan" "docker-compose.gpu.override.yaml"
assert_not_contains "$no_gpu_plan" "verify /clock and key topics"

planning_demo_plan=$("$SCRIPT" --dry-run --planning-demo)
assert_contains "$planning_demo_plan" "--env-file carla-simulation.env --env-file carla-simulation.planning-demo.env"
assert_contains "$planning_demo_plan" "-f docker-compose.planning-demo.override.yaml"
assert_contains "$planning_demo_plan" "up -d --force-recreate --no-deps carla-ros-bridge"

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT
fake_bin="$tmp_dir/bin"
mkdir -p "$fake_bin" "$tmp_dir/home/autoware_map/sample-map-planning"

cat > "$fake_bin/docker" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ "$1" == "logs" && "$*" == *"carla-ros-bridge"* ]]; then
  printf 'All objects spawned.\n'
  exit 0
fi

if [[ "$1" == "exec" ]]; then
  command=${*: -1}
  case "$command" in
    *"topic echo --once /clock"*)
      printf 'clock: ok\n'
      exit 0
      ;;
    *"topic list"*)
      case "${FAKE_TOPICS_MODE:-missing}" in
        delayed)
          count=0
          if [[ -f "${FAKE_TOPIC_COUNT:?}" ]]; then
            count=$(<"$FAKE_TOPIC_COUNT")
          fi
          count=$((count + 1))
          printf '%s\n' "$count" > "$FAKE_TOPIC_COUNT"
          if ((count == 1)); then
            printf '/clock\n'
          else
            printf '/clock\n/carla/status\n/carla/ego_vehicle/lidar\n/carla/ego_vehicle/rgb_front/image\n/planning/trajectory\n/control/command/control_cmd\n/vehicle/status/velocity_status\n'
          fi
          ;;
        *)
          printf '/clock\n'
          ;;
      esac
      exit 0
      ;;
  esac
fi

exit 0
EOF

cat > "$fake_bin/timeout" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF

chmod +x "$fake_bin/docker" "$fake_bin/timeout"

if HOME="$tmp_dir/home" PATH="$fake_bin:$PATH" MAP_PATH="$tmp_dir/custom-map" \
    "$SCRIPT" --no-gpu --skip-verify >"$tmp_dir/map-output" 2>&1; then
  fail "expected caller-provided MAP_PATH to be validated"
fi
map_output=$(<"$tmp_dir/map-output")
assert_contains "$map_output" "Map path not found: $tmp_dir/custom-map"

if HOME="$tmp_dir/home" PATH="$fake_bin:$PATH" RUNTIME_VERIFY_TIMEOUT=1 RUNTIME_VERIFY_INTERVAL=1 \
    "$SCRIPT" --no-gpu >"$tmp_dir/output" 2>&1; then
  fail "expected verification to fail when required topics are missing"
fi

if ! HOME="$tmp_dir/home" PATH="$fake_bin:$PATH" RUNTIME_VERIFY_TIMEOUT=3 RUNTIME_VERIFY_INTERVAL=1 \
    FAKE_TOPICS_MODE=delayed FAKE_TOPIC_COUNT="$tmp_dir/topic-count" \
    "$SCRIPT" --no-gpu >"$tmp_dir/delayed-output" 2>&1; then
  fail "expected verification to retry until required topics are present"
fi

printf 'PASS: start-carla-simulation.sh tests\n'
