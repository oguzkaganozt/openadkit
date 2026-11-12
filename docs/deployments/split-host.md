# Split-host Simulation

!!! warning "Experimental"
    Split-host nodes may change in a minor release. See
    [Compatibility](../releases/compatibility.md#experimental).

Run the Autoware stack on one lab machine and the simulator on another, bridged
over Zenoh. A deployment keeps its name and declares its **nodes** in
`deployment.json`; each machine starts one node with `--node`:

- `scenario-simulation`: `--node autoware` on one host, `--node scenario` on
  the other.
- `carla-simulation`: `--node autoware` on one GPU host, `--node carla` on
  the other.

Without `--node`, the deployment runs on one host as usual.

## How It Works

Each node runs two Compose files, named in the manifest: `compose.<node>.yaml`
holds the node's services, and `compose.zenoh.yaml` adds the Zenoh bridge with
the deployment's `config/zenoh.json5` allowlist. The CLI only selects the
node's files and passes its `rosDomainId` as
`OPENADKIT_ROS_DOMAIN_ID`; it adds no service of its own. The allowlist is one
of the node's `requiredFiles`, so a missing or symlinked file fails validation
before any container starts.

Each node is isolated: its own Compose project
(`openadkit-<deployment>_<node>`), container names and ROS domain. The nodes
see each other only through the Zenoh bridge, so both can also run on **one
machine** for testing, as long as each listens on its own port (see
[below](#configure-the-bridge-endpoints)).

DDS stays on loopback (`CYCLONEDDS_NETWORK_INTERFACE=lo`) in the node's
containers and in the bridge; a node ignores another interface in the host
settings file. Only the ROS traffic on the deployment's
[allowlist](#allowlist) crosses Zenoh: simulation time, vehicle status and
commands, transforms, AD API calls, the enabled sensors and what the visualizer
shows. Map blobs and camera images are not routed.

!!! warning "Evidence scope"
    - **In CI:** both node views of each deployment validate, and Scenario
      Simulation's split evidence cell runs its two nodes on one hosted runner.
      The sample scenario passes over Zenoh, and the scenario node's ROS domain
      sees only the bridged topics, no Autoware nodes. CARLA is exempt from CI
      evidence.
    - **By hand, on a lab pair:** sample scenarios pass, and a CARLA goal
      reaches `ArrivedGoal` over the bridge.
    - **Open:** bridge restart resilience, and recorded CARLA throughput and
      latency.

    One-runner evidence is not a general two-host, WAN or vehicle claim; see
    the [Evidence Policy](../releases/evidence.md).

## Prerequisites

On both hosts:

- Host setup as in the [Quickstart](../getting-started/index.md).
- The same Open AD Kit release and ROS distro.
- Layer-2/3 connectivity between the hosts and `7447/tcp` open **only**
  between them. An allowlist is not authentication; do not expose the port to
  a WAN.

Fetch data on the hosts that mount it:

```bash
openadkit fetch scenario-simulation   # both hosts (the runner bind-mounts MAP_PATH)
openadkit fetch carla-simulation      # Autoware host only
```

## Configure the Bridge Endpoints

Create or edit `~/.config/openadkit/<deployment>.env` on each host. Use the
host's LAN IP, not `0.0.0.0`:

| Host | Variables |
| --- | --- |
| Autoware (`--node autoware`) | `ZENOH_LISTEN=tcp/<autoware-host-ip>:7447` |
| Simulator (`--node scenario` or `--node carla`) | `ZENOH_LISTEN=tcp/<sim-host-ip>:7447` and `ZENOH_PEER=tcp/<autoware-host-ip>:7447` |

The Autoware node only listens and starts first. `validate` and `run` on the
connecting node fail fast when `ZENOH_PEER` is unset; `stop`, `status` and
`logs` never need either variable.

To run both nodes on one machine, pass the endpoints per command instead, with
a separate port for each node:

```bash
ZENOH_LISTEN=tcp/127.0.0.1:7447 openadkit run scenario-simulation --node autoware
ZENOH_LISTEN=tcp/127.0.0.1:7448 ZENOH_PEER=tcp/127.0.0.1:7447 \
  openadkit run scenario-simulation --node scenario
```

## Scenario Simulation

Start Autoware first, then the scenario host:

```bash
openadkit run scenario-simulation --node autoware   # Autoware host
openadkit run scenario-simulation --node scenario   # scenario host
```

The runner waits up to `SCENARIO_READY_TIMEOUT` for Autoware over Zenoh before
it launches the scenario. Results are written on the **scenario** host under
`~/openadkit-output/scenario-simulation/results`. The visualizer runs there
too, so RViz takes no CPU or GPU from Autoware on the edge.

## CARLA

Both hosts need an NVIDIA GPU. Start Autoware first, then the CARLA host:

```bash
openadkit run carla-simulation --node autoware   # Autoware host
openadkit run carla-simulation --node carla      # CARLA host
```

CARLA RPC (`127.0.0.1:2000`) and map loading stay local to the CARLA host.
The interface publishes simulation time, the enabled LiDAR, IMU and GNSS
sensors, vehicle status and transforms; Autoware publishes control commands.
Cameras are disabled in `sensor_mapping.yaml`; enabling them requires an
allowlist and throughput update. The visualizer runs on the CARLA host, where
the raw LiDAR already originates.

## Allowlist

Each deployment ships its Zenoh allowlist in
`deployments/<deployment>/config/zenoh.json5`, mounted into the bridge of
every node. Entries are full-name regular expressions, not globs. Both hosts
use the same file, since either side can own an endpoint. Review the list
before routing anything new.

- **The visualizer's topics** are on both allowlists: planning and control
  output, objects, the vector map marker, `/robot_description` and the AD API
  (`/api/.*`) its panels use. Zenoh sends a topic across only when the other
  host subscribes to it, so without a visualizer these stay on the edge.
- **CARLA's processed point clouds** cross at 2 Hz (`pub_max_frequencies`);
  the point cloud map is not bridged.
- **`/sensing/imu/imu_data`** of the simple sensor simulator is on the
  scenario allowlist because autonomous emergency braking and autonomous-mode
  availability on the Autoware host depend on it. Without it the vehicle stays
  in `PLANNING` and the scenario times out.

The split evidence cell checks that every allowlisted topic exists in one of
the two graphs, so an Autoware rename fails CI instead of silently stopping a
topic. CI cannot run CARLA: check its allowlist against the live graph of a
two-host run after an Autoware update.

## Latency and Timing

Cross-host simulation is timing sensitive. With a large round-trip time the
TF stream jitters and control nodes log transform or collision-detector
warnings even when scenarios still pass. Keep both hosts on the same lab LAN;
WAN and VPN links are best-effort and are not the supported setup.

## Lifecycle Notes

- `status`, `logs`, `restart`, `shell`, `record` and `stop` find the running
  node from its Compose project, so you normally omit `--node`. When several
  nodes of one deployment run on the same machine, `status` and `stop` act on
  all of them; pass `--node` to choose one for the other commands.
- Running a node that is already up updates it in place. Starting the
  single-host deployment while a node is running, or a node while the
  single-host deployment is running, is refused: stop it first.
- With `--verbose`, the printed Compose command shows the node's files, env
  files and project name.
- The visualizer is loopback-only on the simulator host (`WEBSOCKIFY_BIND`);
  reach it from another desk through an SSH tunnel.
- Do not restart a single bridge or interface container while the split is
  running: route churn can leave a bridged topic half-connected. Stop and
  start the node instead (see [Troubleshooting](#troubleshooting)).

## Troubleshooting

If RViz shows no **Auto** button and
`/api/operation_mode/change_to_autonomous` answers "The target mode is not
available", a bridged vehicle-status topic has stopped flowing:

- **Diagnosis** on the Autoware host: a state monitor logs a bridge topic
  timeout (for example `/vehicle/status/steering_status topic is timeout`),
  and `/system/command_mode/availability` reports autonomous mode unavailable.
- **Cause:** restarting a single bridge or interface container in a running
  split can leave Zenoh routes half-created (a route is removed and not
  recreated), so the topic no longer crosses.
- **Remedy:** stop the deployment on both hosts and start the nodes again
  (`openadkit stop`, then `openadkit run <deployment> --node ...`). A clean
  restart restores the routes.
