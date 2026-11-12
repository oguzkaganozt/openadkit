# Evidence Policy

A release promotes an existing build. It does not rebuild images or relax its
tests: stable releases and release candidates both require **a successful
evidence run that passed every cell for the promoted build**.

## What the Gate Checks

Before creating a tag, release validation looks for an
`evidence-summary-<build_tag>` artifact and accepts it only when:

1. **The run succeeded:** it is a completed, successful run of
   `.github/workflows/evidence.yaml` on the branch that built the release.
2. **It tested this build:** the summary names the promoted build tag, and it
   tested the build's own commit, not another commit against its images.
3. **Every cell passed:** the summary result is `PASSED`. A cell passes only
   when every level it runs passes, and a missing expected cell fails the run.

A passing rerun may supersede a failed run; a failed run never counts. There is
no release bypass input. The release also requires the latest full scan of the
build to pass.

## Cells and Levels

Evidence cells are enumerated from the deployment manifests, one per ROS distro
and topology:

| Deployment | Distros | Topologies |
|------------|---------|------------|
| Planning Simulation | Humble, Jazzy | Single host; also under Podman and systemd with the [AutoSD](../platforms/autosd.md) units |
| Scenario Simulation | Humble, Jazzy | Single host; two isolated nodes on one host |
| Safety Island Simulation | Humble, Jazzy | Single host, with the pinned Safety Island release over `domain_bridge` |
| `example-kit` | Humble, Jazzy | Single host: a kit made with `openadkit new` on Planning Simulation, plus a fixture that uses every extension point and its own vehicle and sensor kit packages |

Each cell runs these levels on a fresh stack, started with
`openadkit run --no-visualizer`:

- **L0:** manifests and Compose configuration validate. One cell per distro
  also checks that the images' launch files read every launch argument the
  deployments pass, the exempt deployments included: `ros2 launch` ignores an
  argument it does not know, so a renamed Autoware argument would otherwise do
  nothing without any error.
- **L1:** `openadkit run` returns: the deployment's healthchecks pass, so its
  ROS interfaces are present and its topics publish.
- **L2:** the deployment's verify step passes (`openadkit run --verify`): the
  Planning Simulation ego arrives at its goal, or the scenarios pass, plus the
  split-node checks.
- **L3:** the example kit only: the development loop on the running stack. Its
  C++ package changes, `openadkit build` builds it, `openadkit restart` from
  another directory recreates the services, and the stack publishes the change.

The example kit gates a release like every other cell: it shows that each kit
extension point works on the build. It does not verify integrators' own kits.

The workflow retries a failed cell once. A cell that still fails fails the run
and blocks the release.

## What Evidence Does Not Cover

- **Other platforms.** Every cell runs on a hosted `linux/amd64` runner. Images
  are also built and scanned for arm64, but that is not arm64 runtime evidence,
  nor two-machine LAN, GPU, HIL or vehicle evidence.
- **GPU modes.** Planning Simulation's cells run its CPU mode. Its GPU mode
  (`--gpu`, the Diffusion Planner on `planning-cuda`) validates in CI (L0) and
  is checked by hand on a GPU host.
- **Real-time behavior.** A 4-vCPU hosted runner cannot run Autoware in real
  time: the ego drives late, and the bundled samples take about three times as
  long as on a 16-vCPU host. The Scenario Simulation cells therefore run at
  half speed (`GLOBAL_REAL_TIME_FACTOR=0.5`, with `GLOBAL_TIMEOUT=400`
  wall-clock seconds) through the cell's host settings file, so they test the
  scenarios rather than the runner's size.

## CI Exemptions

CARLA Simulation requires a GPU, and Logging Simulation has no hosted evidence
cell yet. Their deployment manifests carry a reasoned `evidence.exempt` entry.
They remain in the bundle, are listed in the release metadata and notes, and
the CLI warns when they run. **An exemption is not runtime evidence.**

Adding an exemption is a reviewed source change, not a release-time override.
Do not use it to hide a known failure in a normally tested cell.

## Autoware and ROS Distro Decisions

Every release, stable or candidate, is a build of `main` (or of a
`release/X.Y` branch that fixes an older line) on the Autoware release tag in
`.github/autoware.ref`. The release records that Autoware version; the build's
`autoware-lock.repos`, resolved SHA and upstream image digests record the
input.

- **Autoware:** pin the latest stable Autoware release at the release cut. If
  it has a blocking issue, keep the previous verified pin and explain the
  exception, date and follow-up in the release notes. A fix that is already
  upstream can be
  [backported](../development/release-process.md#backporting-an-autoware-fix)
  instead.
- **ROS distro:** `defaultRosDistro` in the promoted `openadkit.json` selects
  the default, and the evidence cells of every declared distro must pass. The
  gate never switches from Humble to Jazzy or drops a failing distro by itself:
  to change the supported distros, update the manifests in a reviewed change
  and build and test that revision.

## Metadata and Verification Report

`release-plan.json` seals the selected evidence summary (result, build, commit,
run URL and cells) before packaging. `release-metadata.json` includes that same
evidence, the BOM and the CI exemptions. The bundle, installer, plan and
metadata receive build provenance from the release workflow.

The verification table in the release notes shows the passing-cell count,
readiness time, arrival time and peak memory of that build. A release never
searches older runs or releases; its notes depend only on the release plan.
Missing metrics are shown as `-`, never replaced with zeroes.

See [Verify a Release](verification.md) to check a release yourself, and the
[Evidence Workflow](../development/evidence-workflow.md) for how the cells run.
