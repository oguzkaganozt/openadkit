# Evidence and Release Policy

A release promotes an existing build. It does not rebuild images or silently
relax its tests. Both stable releases and release candidates require **a
successful evidence run that passed every cell for the promoted build**.

## What the gate checks

Before creating a tag, the release validation job looks for an
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

## Cells and levels

Evidence cells are enumerated from the source deployment manifests:

| Deployment | Distros | Topologies |
|------------|---------|------------|
| Planning Simulation | Humble, Jazzy | Single host; also under Podman and systemd with the [AutoSD](../platforms/autosd/index.md) units |
| Scenario Simulation | Humble, Jazzy | Single host; two isolated nodes on one host |
| `example-kit`: a kit made with `openadkit new`, plus a fixture that uses every extension point | Humble, Jazzy | Planning Simulation extended with the fixture's C++ overlay |
| Safety Island Simulation | Humble, Jazzy | Planning Simulation driven by the pinned Safety Island release over `domain_bridge` |

The example kit gates a release like every other cell: it shows that each kit
extension point works on the build. It does not verify integrators' own kits.

All currently run on GitHub-hosted `linux/amd64` runners. Image build and scan
coverage includes the inventory's other architectures; this must not be
presented as arm64 runtime, two-machine LAN, GPU, HIL or vehicle evidence.

- **L0:** manifests and Compose configuration validate.
- **L1:** `openadkit run` returns: the deployment's healthchecks pass, so its
  ROS interfaces are present and its topics publish.
- **L2:** the deployment's verify step passes (`openadkit run --verify`): the
  Planning Simulation ego arrives at its goal, or the scenarios pass, plus the split-node
  checks. Each run starts a fresh stack.
- **L3:** the example kit only: the development loop on the running stack. Its
  C++ package changes, `openadkit build` builds it, `openadkit restart` from
  another directory recreates the services, and the stack publishes the change.

The workflow retries a failed evidence cell once. A cell that still fails fails
the run and blocks a release. The cells start deployments with
`openadkit run --no-visualizer`.

A 4-vCPU GitHub-hosted runner cannot run Autoware in real time: the ego
drives late and the bundled samples take about three times as long as on a
16-vCPU host. The scenario-simulation cells therefore run the simulation at
half speed (`GLOBAL_REAL_TIME_FACTOR=0.5`, with `GLOBAL_TIMEOUT=400` wall-clock
seconds) through the cell's host settings file, so they test the scenarios
rather than the runner's size. Investigate a cell that still fails after the
workflow's retry.

## Testing a pull request

A pull request that changes an image's inputs builds the affected images,
amd64 only, for both distros. A pull request from this repository pushes them
to the CI package `openadkit-ci`, completes the build there with its base
branch's other images, copied by digest, and runs the cells on that build
before merge. A fork's pull request cannot push; its images are checked at the
build and scan only, and run in the cells after merge.

A change that rebuilds no image, such as a deployment setting, the CLI or a
check, runs the cells against an existing build:

- A pull request that touches `deployments/`, `cli/` or the evidence checks
  runs them against its base branch's latest successful build.
- A dispatch of `evidence.yaml` with `source_ref` tests that branch or commit;
  `build_tag` defaults to the dispatched branch's latest successful build.

The cells take the deployments, CLI and checks from the tested commit and the
images from the build. A pull request's run is not release evidence: the gate
accepts only a build of the release branch.

## Explicit CI exemptions

CARLA Simulation requires a GPU; Logging Simulation has no hosted runtime
cell. Their deployment manifests contain a reasoned `evidence.exempt` entry.
They remain in the bundle, are listed in release metadata/notes, and the CLI
warns when they run. **An exemption is not runtime evidence.**

Planning Simulation's cells run its CPU mode. Its GPU mode (`--gpu`, the
Diffusion Planner on `planning-cuda`) has no hosted evidence cell; it is checked
on a GPU host and validated (L0) in CI.

Adding an exemption is a reviewed source change, not a release-time override.
Do not use it to hide a known product failure in a normally tested cell.

## Autoware and ROS distro decisions

Pin the latest stable Autoware release at the release cut. If it has a blocking
issue, keep the previous verified stable pin and explain the exception, date
and follow-up in the release notes.

Every release, stable or candidate, is a build of `main` (or of a
`release/X.Y` branch that fixes an older line) on the Autoware release tag in
`.github/autoware.ref`. The release records that Autoware version; the build's
`autoware-lock.repos`, resolved SHA and upstream image digests record the input.

### Backporting an Autoware fix

Autoware releases come months apart. A fix that blocks a release and is
upstream, merged on Autoware's `main` or in an open pull request, can ride on
the pinned release as a patch instead of waiting for the next Autoware release:

1. In the upstream repository, `git format-patch -1 <commit>`, and add a line
   `Upstream: <URL of the commit or pull request>` to its message.
2. Open a pull request into `main` (or the `release/X.Y` branch) that adds it as
   `.github/autoware-patches/<repository>/<NNNN>-<subject>.patch`, where
   `<repository>` is its path under `autoware/src` (a key of
   `autoware-lock.repos`, such as `universe/autoware_universe`). The review is
   the fix's own diff.
3. Every build applies the patches in order right after
   `vcs import`; one that does not apply, or has no `Upstream:` line, fails the
   build. The release lists them under **Backported Autoware fixes**, its
   bundle carries them as `autoware.backports`, and `openadkit version` counts
   them. The Autoware version stays that of the tag.
4. When the branch moves to an Autoware release that contains the fix, delete
   the patch.

`defaultRosDistro` in the promoted `openadkit.json` explicitly selects the ROS
distro, and its required evidence cells must pass.
The gate does not automatically switch from Humble to Jazzy or remove a failing
distro. To change supported distros, update the manifests in a reviewed source
change and build/test that revision. Humble remains the initial default.

## Metadata and verification report

`release-plan.json` seals the selected evidence summary (result, build, commit,
run URL and cells) before packaging. `release-metadata.json` includes that same
evidence, the BOM and the CI exemptions. Bundle, installer, plan and metadata
receive release-workflow build provenance.

The verification table shows passing-cell count, readiness time, arrival time
and peak memory for the current build. Release never searches older runs or
releases; its notes depend only on the release plan. Missing metrics are shown
as `-`, never replaced with zeroes.

See [Verify a Release](verification.md) and
[Run the Evidence Workflow](../development/evidence-workflow.md).
