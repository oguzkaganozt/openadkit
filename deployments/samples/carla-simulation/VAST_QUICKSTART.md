# Temporary Vast.ai CARLA Quickstart

This is a temporary runbook for reproducing the CARLA simulation sample on fresh Vast.ai KVM instances. Delete this file before merging the branch into `main`.

## 1. Rent a Pure VM Instance

Search for a verified on-demand KVM offer with a full GPU, not a shared GPU slice:

```bash
vastai search offers 'verified=true rentable=true rented=false vms_enabled=true num_gpus=1 gpu_frac=1 gpu_ram>=24 cpu_cores_effective>=16 cpu_ram>=32 disk_space>=150 driver_version>=570.0.0' \
  --storage 150 \
  --limit 20 \
  -o 'dph,reliability-'
```

Create the VM with the Vast Ubuntu 22.04 KVM image:

```bash
vastai create instance <OFFER_ID> \
  --image docker.io/vastai/kvm:ubuntu_cli_22.04-2025-05-16 \
  --disk 150 \
  --ssh \
  --direct \
  --label openadkit-vm \
  --cancel-unavail
```

Get the direct SSH endpoint. Prefer this over the proxy host/port shown in `show instances` if SSH is refused:

```bash
vastai ssh-url <INSTANCE_ID>
```

Current known-good shape:

```text
ssh://root@<PUBLIC_IP>:<DIRECT_PORT>
```

## 2. Verify Base VM Runtime

Connect as `root` using the direct endpoint:

```bash
ssh root@<PUBLIC_IP> -p <DIRECT_PORT>
```

Verify resources and NVIDIA Docker support:

```bash
nproc
free -h
df -h /
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
docker --version
docker compose version
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 \
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
```

Expected shape:

```text
RTX 4090 or better
24GB+ VRAM
32GB+ RAM
150GB disk
NVIDIA driver 570+
Docker Compose v2
```

## 3. Bootstrap User, Repos, and Map

Run these commands as `root` on the VM:

```bash
id openadkit >/dev/null 2>&1 || useradd -m -s /bin/bash openadkit
usermod -aG sudo,docker openadkit
install -d -o openadkit -g openadkit /workspace
```

If `git`, `unzip`, or `pip` are missing, install them. If the default apt mirrors hang, use a nearby mirror or retry later:

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  git unzip python3-pip curl ca-certificates
```

Clone this branch and the CARLA ROS bridge source. The bridge clone must include submodules or `carla_msgs` will be missing at runtime:

```bash
runuser -u openadkit -- bash -lc \
  'git clone --branch feat/carla-simulation-sample https://github.com/autowarefoundation/openadkit.git /workspace/openadkit'

runuser -u openadkit -- bash -lc \
  'git clone --recurse-submodules https://github.com/carla-simulator/ros-bridge.git /home/openadkit/carla-ros-bridge'
```

Download the planning sample map. `gdown` v6 accepts the file ID as a positional argument; older `--id` examples fail:

```bash
runuser -u openadkit -- bash -lc \
  'python3 -m pip install --user gdown && \
   mkdir -p /home/openadkit/autoware_map && \
   /home/openadkit/.local/bin/gdown 1499_nsbUbIeturZaDj7jhUownh5fvXHd -O /home/openadkit/autoware_map/sample-map-planning.zip && \
   unzip -o -d /home/openadkit/autoware_map /home/openadkit/autoware_map/sample-map-planning.zip && \
   ls /home/openadkit/autoware_map/sample-map-planning'
```

## 4. Build the Local CARLA ROS Bridge Image

Copy the patched Dockerfile into the bridge checkout:

```bash
runuser -u openadkit -- bash -lc \
  'cp /workspace/openadkit/deployments/samples/carla-simulation/Dockerfile.carla-ros-bridge.humble /home/openadkit/carla-ros-bridge/Dockerfile.openadkit'
```

Build with default Ubuntu mirrors:

```bash
runuser -u openadkit -- bash -lc \
  'docker build \
     --build-arg CARLA_VERSION=0.9.15 \
     --build-arg ROS_DISTRO=humble \
     -t local/carla-ros-bridge:0.9.15-humble \
     -f /home/openadkit/carla-ros-bridge/Dockerfile.openadkit \
     /home/openadkit/carla-ros-bridge'
```

If `apt-get update` hangs or fails against `security.ubuntu.com` or `archive.ubuntu.com`, rebuild with a regional Ubuntu mirror. Spain worked on the known-good VM:

```bash
runuser -u openadkit -- bash -lc \
  'docker build \
     --build-arg CARLA_VERSION=0.9.15 \
     --build-arg ROS_DISTRO=humble \
     --build-arg UBUNTU_APT_MIRROR=http://es.archive.ubuntu.com/ubuntu \
     --build-arg UBUNTU_SECURITY_APT_MIRROR=http://es.archive.ubuntu.com/ubuntu \
     -t local/carla-ros-bridge:0.9.15-humble \
     -f /home/openadkit/carla-ros-bridge/Dockerfile.openadkit \
     /home/openadkit/carla-ros-bridge'
```

The build must include `carla_msgs`:

```text
Starting >>> carla_msgs
Summary: 6 packages finished
```

If `carla_msgs` is missing, fix the bridge checkout and rebuild:

```bash
runuser -u openadkit -- bash -lc \
  'cd /home/openadkit/carla-ros-bridge && git submodule update --init --recursive && test -f carla_msgs/package.xml'
```

## 5. Start CARLA and Wait for RPC

Run compose as `openadkit`, not `root`, so `$HOME` in `carla-simulation.env` resolves to `/home/openadkit`:

```bash
runuser -u openadkit -- bash -lc \
  'cd /workspace/openadkit/deployments/samples/carla-simulation && \
   docker compose --env-file carla-simulation.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml up -d carla'
```

Wait until CARLA listens on RPC port `2000`:

```bash
for i in $(seq 1 120); do
  ss -ltn | grep -q ':2000 ' && break
  sleep 5
done
```

## 6. Start the Bridge, Then the Stack

Start or recreate the bridge after CARLA is listening:

```bash
runuser -u openadkit -- bash -lc \
  'cd /workspace/openadkit/deployments/samples/carla-simulation && \
   docker compose --env-file carla-simulation.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml up -d --force-recreate carla-ros-bridge'
```

Wait for the bridge to spawn the ego vehicle and sensors:

```bash
docker logs -f carla-ros-bridge
```

Expected log lines:

```text
Created EgoVehicle(id=...)
All objects spawned.
```

Start the rest of the OpenADKit services:

```bash
runuser -u openadkit -- bash -lc \
  'cd /workspace/openadkit/deployments/samples/carla-simulation && \
   docker compose --env-file carla-simulation.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml up -d'
```

## 7. Verify Runtime State

Check containers:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

Check restart counts:

```bash
docker inspect -f '{{.Name}} restart={{.RestartCount}} state={{.State.Status}}' carla carla-ros-bridge
```

Check topics and `/clock`:

```bash
docker exec autoware-map bash -lc \
  'source /opt/ros/humble/setup.bash && \
   timeout 10 ros2 topic list | grep -E "^/(clock|carla/status|carla/ego_vehicle/(lidar|rgb_front/image)|planning/trajectory|control/command/control_cmd|vehicle/status/velocity_status)" || true'

docker exec autoware-map bash -lc \
  'source /opt/ros/humble/setup.bash && timeout 10 ros2 topic echo --once /clock'
```

Expected topics:

```text
/carla/ego_vehicle/lidar
/carla/ego_vehicle/rgb_front/image
/carla/status
/clock
/control/command/control_cmd
/planning/trajectory
/vehicle/status/velocity_status
```

## 8. Open RViz Through a Local Tunnel

From your local machine, create a tunnel to the VM:

```bash
ssh -fN \
  -o ExitOnForwardFailure=yes \
  -L 6080:127.0.0.1:6080 \
  -p <DIRECT_PORT> \
  root@<PUBLIC_IP>
```

Open:

```text
http://localhost:6080/vnc.html
```

Password:

```text
openadkit
```

Verify the tunnel if needed:

```bash
curl -I --max-time 10 http://127.0.0.1:6080/vnc.html
```

Expected response: HTTP `200` from `WebSockify`.

## 9. Recovery Notes

If CARLA restarts after the bridge spawned actors, the bridge can keep stale actor IDs and `/clock` may stop. Evidence looks like:

```text
OdometrySensor could not publish. parent actor ... not found
SpeedometerSensor could not publish. Parent actor ... not found
```

Recover by recreating only the bridge after CARLA is running again:

```bash
runuser -u openadkit -- bash -lc \
  'cd /workspace/openadkit/deployments/samples/carla-simulation && \
   docker compose --env-file carla-simulation.env -f docker-compose.yaml -f docker-compose.gpu.override.yaml up -d --force-recreate carla-ros-bridge'
```

If bridge logs show `ModuleNotFoundError: No module named 'carla_msgs'`, the CARLA ROS bridge was cloned without submodules. Run submodule init and rebuild the bridge image.

If Vast shows `ssh8.vast.ai:<port>` but SSH is refused, run `vastai ssh-url <INSTANCE_ID>` and use the direct `root@<PUBLIC_IP> -p <DIRECT_PORT>` endpoint instead.

## 10. Cleanup

Stop the local SSH tunnel by killing the matching local `ssh -fN -L 6080:127.0.0.1:6080` process.

Destroy old or unused Vast instances to stop billing:

```bash
vastai destroy instance <INSTANCE_ID> -y
```

Before merging this branch to `main`, delete this temporary file:

```bash
rm deployments/samples/carla-simulation/VAST_QUICKSTART.md
```
