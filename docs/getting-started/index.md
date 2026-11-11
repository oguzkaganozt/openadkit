# Quickstart

From zero to a running Autoware planning simulation in about 10 minutes. No GPU is required.

<nav class="oak-quickstart" aria-label="Quickstart steps">
  <ol>
    <li>
      <a href="#get-open-ad-kit">
        <span class="oak-quickstart__number">1</span>
        <span><strong>Get the kit</strong><small>Download or clone</small></span>
      </a>
    </li>
    <li>
      <a href="#set-up-the-host">
        <span class="oak-quickstart__number">2</span>
        <span><strong>Set up the host</strong><small>Configure dependencies</small></span>
      </a>
    </li>
    <li>
      <a href="#run-planning-simulation">
        <span class="oak-quickstart__number">3</span>
        <span><strong>Run simulation</strong><small>Start planning</small></span>
      </a>
    </li>
    <li>
      <a href="#open-the-visualizer">
        <span class="oak-quickstart__number">4</span>
        <span><strong>Open visualizer</strong><small>Inspect the output</small></span>
      </a>
    </li>
    <li>
      <a href="#drive">
        <span class="oak-quickstart__number">5</span>
        <span><strong>Drive</strong><small>Set a route</small></span>
      </a>
    </li>
  </ol>
</nav>

## Prerequisites

- **Ubuntu 22.04 (Jammy) or 24.04 (Noble)** with `sudo` access
- `curl` for the release installer; `python3` and `tar` are preinstalled on
  supported Ubuntu releases
- A web browser: the visualizer runs in it, so no display server is needed

## 1. Get Open AD Kit {: #get-open-ad-kit }

--8<-- "includes/first-release-note.md"

=== "Release bundle"

    The installer verifies the release bundle, installs it to
    `~/.local/share/openadkit` and puts `openadkit` in `~/.local/bin`:

    ```bash
    curl -fsSL https://github.com/autowarefoundation/openadkit/releases/latest/download/openadkit \
      | bash -s -- install
    ```

    If `~/.local/bin` is not on your `PATH`, the installer prints the command to
    add it. For a reproducible install, replace `latest` with a release version
    and pass the same version to `install`:

    ```bash
    curl -fsSL https://github.com/autowarefoundation/openadkit/releases/download/vX.Y.Z/openadkit \
      | bash -s -- install --version vX.Y.Z
    ```

    To check the files yourself before running them, see
    [Verify a Release](../releases/verification.md).

=== "Source checkout"

    ```bash
    git clone https://github.com/autowarefoundation/openadkit.git
    cd openadkit
    ```

    Run the commands below as `./openadkit` from the repository root.

The release bundle holds the CLI and the deployments; images and sample data
are pulled on demand. A source checkout also holds the image sources, CI and
development tools.

## 2. Set Up the Host {: #set-up-the-host }

```bash
openadkit setup --verify
```

Run setup as your normal user; it asks for `sudo` only for host changes. It
installs Docker when the host has none and never replaces an existing engine.
Add `--gpu` for NVIDIA deployments: it also installs the NVIDIA Container
Toolkit and the OpenGL/Vulkan libraries CARLA needs.

--8<-- "includes/docker-group-activation.md"

## 3. Run Planning Simulation {: #run-planning-simulation }

```bash
openadkit run planning-simulation
```

`run` downloads and verifies the sample map, pulls missing images, starts the
services, and returns once Autoware is ready.

--8<-- "includes/ros-distro.md"

## 4. Open the Visualizer {: #open-the-visualizer }

--8<-- "includes/visualizer-remote-access.md"

To open RViz on your own desktop instead of the browser, see
[Visualizer](../components/index.md#visualizer).

## 5. Drive {: #drive }

In RViz, follow the [Autoware planning simulation instructions](https://autowarefoundation.github.io/autoware-documentation/main/demos/planning-sim/lane-driving/#2-set-an-initial-pose-for-the-ego-vehicle) to:

1. Set an **initial pose** for the ego vehicle
2. Set a **goal pose** on the map
3. Watch the vehicle plan and drive the route

## Next Steps

- [Deployments](../deployments/index.md) — scenario testing, rosbag replay, CARLA and Safety Island
- [CLI & Maintenance](cli.md) — runtime controls, configuration, upgrades and cleanup
- [Create a Kit](../deployments/create-a-kit.md) — your own stack on top of a deployment
- [Components](../components/index.md) — the images behind what you just ran
- [Troubleshooting](troubleshooting.md) — when something does not start
