# Troubleshooting

--8<-- "includes/cli-command-context.md"

## A Deployment Fails to Start

1. Check that Docker is running: `docker info`.
2. Check the configuration and the data: `openadkit validate <deployment> --data`.
3. See which services are up: `openadkit status`.
4. Read the logs: `openadkit logs --follow`.

If `run` fails after the containers are created, they keep running so you can
read their logs. Stop them with `openadkit stop`.

## Docker

### Permission denied

Your user must be in the `docker` group. Log out and back in after
`openadkit setup`, or run `newgrp docker`. Do not run `openadkit` with `sudo`.

### Docker Compose is too old

`openadkit setup` stops when Docker is installed but Docker Compose 5.0 or
newer is missing. Install Docker's `docker-compose-plugin`
([instructions](https://docs.docker.com/compose/install/linux/)) and rerun
setup. Ubuntu's own `docker-compose-v2` package is too old.

## Data

### Missing or incomplete maps, rosbags, or models

```bash
openadkit validate <deployment> --data
openadkit fetch <deployment> --force
```

`validate --data` reports each resource as `ok`, `missing`, `incomplete` or
`outdated`; add `--gpu` to include the data of a GPU mode, such as Logging
Simulation's CenterPoint models. `fetch` always includes it. `--force` only
replaces data the CLI installed; remove data you placed yourself, then run
`openadkit fetch <deployment>`. See
[Downloaded Data](cli.md#downloaded-data).

## GPU

### NVIDIA Container Toolkit not detected

- Install it with `openadkit setup --gpu --verify`.
- Check the GPU: `nvidia-smi` and `nvidia-ctk --version`.
- Restart Docker: `sudo systemctl restart docker`.

### Perception is slow

The default perception image runs on CPU. For CUDA perception, run Logging
Simulation with `--gpu` on an amd64 host with an NVIDIA GPU. The CUDA image does
not fall back to CPU.

## Visualizer and Network

### Blank visualizer

Wait 10 to 30 seconds after `run`, then reload the page. If it stays blank,
check `openadkit logs --follow`.

### noVNC says "failed to connect"

Open the page over `http://`. The visualizer serves plain HTTP unless you give
it a certificate (`NOVNC_CERT`, `NOVNC_KEY`); with one, open it over
`https://`.

### Port 6080 already in use

Port 6080 serves the visualizer. Stop the service that holds the port. The
deployments use host networking, so a `ports:` mapping in `compose.yaml`
has no effect.

### Point clouds arrive at a lower rate than they are published

Large messages need large UDP buffers between the containers.
`deployments/shared/cyclonedds.xml` requests them, and `openadkit setup` raises
the kernel limits that cap them (`/etc/sysctl.d/99-openadkit-dds.conf`). Check
the limit and whether the kernel drops packets:

```bash
sysctl net.core.rmem_max      # 2147483647 after setup
nstat -az UdpRcvbufErrors     # a growing count means drops
```

### ROS 2 nodes on another machine cannot see the stack

DDS stays on loopback by default. To reach other hosts, set
`CYCLONEDDS_NETWORK_INTERFACE` to the exact LAN or VPN interface name in your
[host settings file](cli.md#configuration)
(`~/.config/openadkit/<deployment>.env`):

```bash
CYCLONEDDS_NETWORK_INTERFACE=eth0
```

This applies to single-host runs; a split-host role always keeps DDS on
loopback and reaches the other host through its Zenoh bridge.
`ROS_DOMAIN_ID` separates traffic but provides no authentication or encryption.

## Getting Help

- [GitHub Issues](https://github.com/autowarefoundation/openadkit/issues)
- [Autoware Foundation Discord](https://discord.gg/Q94UsPvReQ)
