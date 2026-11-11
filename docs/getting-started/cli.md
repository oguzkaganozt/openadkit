# CLI & Maintenance

The commands you need after the first run. `openadkit --help` and
`openadkit <command> --help` list every option.

--8<-- "includes/cli-command-context.md"

| Command | What it does |
|---------|--------------|
| [`list`, `run`](#run-a-deployment) | List the deployments, and start one and wait until it is ready |
| [`status`, `logs`, `shell`, `record`](#runtime-controls) | Inspect the running deployment and record its topics |
| [`restart`](#restart) | Apply changed settings, config and overlay workspaces |
| [`stop`](#runtime-controls) | Stop and remove the running deployment |
| [`validate`, `config`](#validate-before-running) | Check a deployment, or print its Compose model, without starting it |
| [`fetch`, `clean`](#downloaded-data) | Download or delete a deployment's data |
| [`new`, `build`](#your-own-kit) | Create a kit and build its overlay workspace |
| [`setup`](index.md#set-up-the-host) | Install the host dependencies |
| [`install`, `upgrade`](#upgrading), [`uninstall`](#uninstall) | Install, move between and remove releases |
| [`version`](#names-directories-and-output) | Show the installed release and its Autoware release |

## Run a Deployment

```bash
openadkit list                                    # the deployments you can run
openadkit run planning-simulation
openadkit run planning-simulation --verify        # then run its end-to-end check
openadkit run planning-simulation --pull always   # refresh the images first
openadkit run planning-simulation --no-visualizer
```

`run` downloads missing data, pulls missing images, starts the services and
returns once the deployment is ready.

- **Ready** means the services' healthchecks pass, for example once the AD API
  is up (`READINESS_CHECKS` in the deployment's `settings.env`). `run` then
  watches the services for 10 seconds and fails if one crashes, restarts, exits
  or turns unhealthy; a one-shot service may finish but not fail.
- **`--verify`** then runs the deployment's verify step, the check CI runs on
  it: Planning Simulation drives the ego from its start to its goal, Scenario
  Simulation waits for the scenarios' result. `run` exits with the step's
  result; the deployment keeps running.
- **`--no-visualizer`** starts everything except the visualizer, for a host
  nobody watches: its software-rendered RViz needs CPU that Autoware lacks on a
  small host. CI evidence runs this way.
- **One deployment runs at a time**, including deployments from other kits,
  even one with the same name. `run` refuses while another is running; stop it
  first with `openadkit stop`. The nodes of one
  [split-host](../deployments/split-host.md) deployment can run together.

Every run writes `results/run.json` in the deployment's output directory: the
version, distro and images it started, the digest of the resolved Compose
model, content digests of the config layers and overlay workspace it mounts,
how long it took to be ready and, with `--verify`, the step's result.

## Runtime Controls

```bash
openadkit status
openadkit logs --follow
openadkit logs map planning        # only these services
openadkit restart                  # apply changed settings, config and overlay workspaces
openadkit restart --all            # recreate the whole deployment
openadkit shell                    # a shell in the api service with ROS sourced
openadkit shell planning ros2 node list
openadkit record /tf /localization/kinematic_state
openadkit stop
```

These act on the deployment running on this host, from any directory, so they
take no deployment name. With several nodes of a split-host deployment on one
host, see [Lifecycle Notes](../deployments/split-host.md#lifecycle-notes).

### Status

Below its services, `status` shows Autoware's state from the AD API and the
visualizer address:

```text
localization initialized
routing      set
mode         stop (autonomous available)
mrm          normal
```

A line reads `no data` while nothing publishes that state yet, for example
before localization starts.

### Restart

`restart` recreates services as `run` started them, with the current settings,
config and overlay workspace, and keeps to the same readiness checks.

- With no service, it recreates every service that takes Open AD Kit config or
  an overlay workspace, and every service whose settings changed. A changed
  parameter file, a rebuilt workspace or a new `settings.env` value applies
  without restarting a simulator such as CARLA; `restart` names the services it
  left running.
- `restart <service>...` recreates only those services.
- `restart --all` recreates the whole deployment, one-shot services included.

### Shell

`shell` sources ROS, Autoware and the overlay workspace like the services'
entrypoint. Give it a service and a command to run one command instead of an
interactive shell.

### Record

`record` writes a rosbag of the named topics (or `--all`) to
`~/openadkit-output/<deployment>/recordings/` (`--output` to change) until
Ctrl+C. It runs as a copy of the running `api` container, so it joins the
deployment's ROS domain and knows the overlay's message types, and the bag
stays on the host when the deployment stops.

## Validate Before Running

```bash
openadkit validate planning-simulation --data
```

`validate` checks the manifest and the Compose configuration without starting
anything. `--data` also reports each data resource as `ok`, `missing`,
`incomplete` or `outdated` and fails on any gap. It follows the same GPU
selection as `run`: `openadkit validate logging-simulation --gpu --data`
includes the CenterPoint models.

`config` prints a deployment's resolved Compose model as JSON, with `validate`'s
`--ros-distro`, `--gpu`, `--node` and `--ws`;
[AutoSD](../platforms/autosd.md) builds on it.

## Configuration

A deployment reads its settings from environment files, in this order (later
files win):

1. `deployments/<name>/settings.env`: the deployment defaults
2. `deployments/<name>/settings.gpu.env`: GPU settings, loaded only with `--gpu`
3. `~/.config/openadkit/<name>.env`: your host settings file

Shell exports do not override variables defined in these files. Put host
settings such as `MAP_PATH` or `REMOTE_PASSWORD` in your host settings file: it
lives outside the release, so upgrades keep it. A source checkout can also
override component images there; release images stay pinned. A kit adds its
own files to this order; see the
[Integrator Guide](../kits/integrator-guide.md#1-settings).

| Directory | Default | Override |
| --- | --- | --- |
| Host settings | `~/.config/openadkit` | `OPENADKIT_CONFIG_DIR` (or `XDG_CONFIG_HOME`) |
| Results and recordings | `~/openadkit-output/<name>/{results,recordings}` | `OPENADKIT_OUTPUT_DIR` |
| Installed releases | `~/.local/share/openadkit` | `OPENADKIT_INSTALL_DIR` |

## Downloaded Data

Maps, rosbags and models live under `~/autoware_map` and `~/autoware_data`.

```bash
openadkit validate planning-simulation --data   # report
openadkit fetch planning-simulation --force     # replace
openadkit clean planning-simulation             # delete, after asking
```

- **`run`** downloads missing data but never replaces an existing data
  directory; `run --force` is not supported.
- **`fetch --force`** replaces incomplete or outdated data. Data is outdated
  when the deployment now declares other content for it, for example a map with
  a new checksum: `run`, `fetch` and `validate --data` then stop and ask for
  `fetch --force`. `fetch` always includes the GPU data.
- **`clean`** lists what it deletes and asks first; `--yes` skips the question,
  as scripts need. It deletes all the data the deployment uses, so a kit or a
  deployment on a base also deletes the base's data (the list says so). The
  next `run` or `fetch` downloads it again.

The CLI marks the data it installs with a `.openadkit-resource.json` file, and
`clean` and `--force` only delete or replace marked data. Data that was already
there, such as a map you copied yourself, is used when it is complete, but the
CLI never deletes or replaces it; move or remove it yourself.

`clean` and `fetch --force` refuse while that deployment is running, or while
any live container mounts the data (including another kit or deployment). If
data usage cannot be checked, they refuse as well.

## Your Own Kit

`openadkit new my-kit [--base DEPLOYMENT]` makes `./my-kit`, a kit on top of a
deployment of this Open AD Kit (Planning Simulation by default) that holds
only your differences. `openadkit build` builds the kit's overlay workspace in
the release's devel image. See [Create a Kit](../kits/create-a-kit.md).

## Upgrading

```bash
openadkit upgrade --check   # report whether a newer stable version exists
openadkit upgrade           # install it
```

The new release is verified and installed next to the old one, and the
`openadkit` launcher is repointed. The previous version stays in the install
directory, so you can roll back:

```bash
openadkit install --version vOLD
```

A version that is already installed becomes the active one as it is, without a
download, so this works offline; `--force` downloads and replaces it. Images of
a version you no longer use stay in Docker until you remove them, for example
with `docker image prune --all`. A source checkout updates with `git pull`
instead.

## Uninstall

Stop running deployments first; `uninstall` refuses while any is running,
because it removes the launcher that `openadkit stop` needs.

```bash
openadkit stop
openadkit uninstall          # keep previously installed versions
openadkit uninstall --all    # remove kept versions too
```

`uninstall` is for release installs; remove a source checkout with Git. It
keeps your host settings in `~/.config/openadkit`, results and recordings in
`~/openadkit-output`, and downloaded data.

## Names, Directories and Output

- **A directory instead of a name:** `validate`, `config`, `fetch`, `run` and
  `clean` also take a deployment's directory, such as `openadkit run ./my-kit`.
  An argument with a `/` or a leading `.` is a directory, and the kit around it
  is used wherever you run the command.
- **Version:** `openadkit version` prints the installed release and the
  Autoware release it pins; in a source checkout, the commit.
- **Scripting:** `list`, `version` and `validate` accept `--json`.
  `validate --json` prints one JSON document also when the deployment is
  invalid (`"valid": false` with the `"error"`).
- **Docker commands:** commands print what they do in plain terms; add
  `--verbose` (or set `OPENADKIT_VERBOSE=1`) to also see the docker commands
  they run, status queries aside.
- **Short name and Tab completion:** `openadkit install` also links `adkit`, a
  short name for the same launcher. Tab completes commands, options and
  deployment names for both names, from the kit around the current directory
  or else the active release; bash-completion (installed on Ubuntu by default)
  loads it from `~/.local/share/bash-completion/completions` in a new shell.
  The installer leaves an `adkit` or a completion file it did not install
  alone, and `openadkit uninstall` removes only its own links.
