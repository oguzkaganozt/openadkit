# Create a Kit

`openadkit new` makes a kit that extends this release and one of its
deployments without copying them, so the kit holds only your differences:

```bash
openadkit new my-kit                       # on top of planning-simulation
openadkit new my-kit --base scenario-simulation
```

--8<-- "includes/cli-command-context.md"

## One Directory, One Deployment

```text
my-kit/
├── openadkit.json
├── deployment.json
├── compose.yaml
├── settings.env
├── config/autoware/
└── overlay_ws/src/
```

The kit's `README.md` explains each file. `openadkit.json` pins the release
(`extends`), and `deployment.json` names the base deployment, whose
architectures, ROS distros, GPU mode, downloads and verify step the kit
inherits; `requirements` may narrow the first three. `compose.yaml` includes the
base's Compose file, with your services below it.

The deployment's name is its key in `openadkit.json`, here `my-kit`;
`deployment.json` does not repeat it. Renaming the directory changes nothing.

## Build, Validate, Run, Stop

```bash
cd my-kit
openadkit build                 # overlay_ws, in the release's devel image
openadkit validate
openadkit run --verify          # start, wait until ready, run the base's verify step
openadkit stop
```

Inside a kit with one deployment the commands need no name. From elsewhere,
name it by its directory: `openadkit run ./my-kit`. A kit on a source checkout
needs `DEVEL_IMAGE` for `build`; see
[Overlay Workspace](kit-guide.md#3-overlay-workspace).

Add `--ros-distro jazzy` to `build`, `validate` and `run` for Jazzy.
`validate` renders the Compose model without starting anything; it is not
runtime or ABI evidence, so finish with `run --verify`.

Every release tests a kit made this way: the
[example kit](../releases/evidence.md#cells-and-levels) exercises each
extension point on Humble and Jazzy.

## Make a Change

A config override changes a parameter without a build. Put the file with only
the keys you change under `config/autoware/`, at the path it has in its
package's share directory, then recreate the services that use it:

```bash
mkdir -p config/autoware/autoware_launch/config/planning/scenario_planning/common
$EDITOR config/autoware/autoware_launch/config/planning/scenario_planning/common/common.param.yaml
openadkit restart               # the services with config overrides or settings that changed
```

A package change needs a build and a restart of the service that runs it:

```bash
openadkit build
openadkit restart my-node
```

[Develop and Debug](develop-and-debug.md) times that loop and shows how to look
into the running services.

## Where Changes Go

Keep parameter changes in `config/autoware/` and packages in `overlay_ws/`
rather than mounting over `/opt/autoware` or replacing a base service's
command. The [Kit Guide](kit-guide.md) is the reference for the
settings order, config overrides, the overlay workspace, extra services and
image replacement.
