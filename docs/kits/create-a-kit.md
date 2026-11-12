# Create a Kit

`openadkit new` makes a kit that extends this Open AD Kit and one of its
deployments without copying them, so the kit holds only your differences:

```bash
openadkit new my-kit                       # on top of planning-simulation
openadkit new my-kit --base scenario-simulation
```

## One Directory, One Deployment

```text
my-kit/
├── openadkit.json
├── deployment.json
├── docker-compose.yaml
├── settings.env
├── config/autoware/
└── overlay_ws/src/
```

- `openadkit.json` pins the Open AD Kit release (`extends`), lists extra images you pin
  (`externalImages`), and points the `my-kit` deployment at `"."`, this same
  directory.
- `deployment.json` names the base deployment. Compose reads
  `docker-compose.yaml` unless `compose.files` names others. Architecture, ROS
  distro, GPU, downloads and the verify step are inherited; `requirements` may
  narrow the first three.
- `docker-compose.yaml` includes `${OPENADKIT_BASE_DEPLOYMENT}/docker-compose.yaml`;
  add your services below it. `OPENADKIT_ROOT` names the release's root, for
  its shared assets.
- `settings.env` holds only the values you change, such as `VEHICLE_ID`.
- `config/autoware/` holds parameter overrides for Autoware packages.
- `overlay_ws/src/` holds your ROS packages.

The deployment's name is its key in `openadkit.json`, here `my-kit`;
`deployment.json` does not repeat it. Renaming the directory changes nothing.

## Pin the Release

`openadkit new` from an installed release writes its version, such as
`"extends": "v2.0.0"`; the kit then runs with that release's own launcher.
From a source checkout it writes the checkout's path. To move to another
release, change `extends`; the next command that acts on the kit, such as
`validate` or `run`, downloads that release if it is missing.

## Build, Validate, Run, Stop

```bash
cd my-kit
openadkit build                 # overlay_ws, in the release's devel image
openadkit validate
openadkit run --verify          # start, wait until ready, run the base's end-to-end check
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

## Where Changes Go

Keep parameter changes in `config/autoware/` and packages in `overlay_ws/`
rather than mounting over `/opt/autoware` or replacing a base service's
command. The [Kit Guide](kit-guide.md) is the reference for the
settings order, config overrides, the overlay workspace, extra services and
image replacement.
