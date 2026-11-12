# Evidence Workflow

`.github/workflows/evidence.yaml` runs the
[evidence cells](../releases/evidence.md#cells-and-levels) against one build and
publishes the run's summary. It runs after every successful `build-all-images`
run on `main` or a `release/X.Y` branch, which is the run a release of that
build needs.

## Testing a Pull Request

A pull request that changes an image's inputs builds the affected images,
amd64 only, for both distros. A pull request from this repository pushes them
to the CI package `openadkit-ci`, completes the build there with its base
branch's other images, copied by digest, and runs the cells on that build
before merge. A fork's pull request cannot push; its images are checked at the
build and scan only, and run in the cells after merge.

A pull request runs the amd64 cells only. A build of the branch runs the cells
of every architecture.

A change that rebuilds no image, such as a deployment setting, the CLI or a
check, runs the cells against an existing build:

- A pull request that touches `deployments/`, `cli/` or the evidence checks
  runs them against its base branch's latest successful build.
- A dispatch of `evidence.yaml` with `source_ref` tests that branch or commit;
  `build_tag` defaults to the dispatched branch's latest successful build.

The cells take the deployments, CLI and checks from the tested commit and the
images from the build. A pull request's run is not release evidence: the gate
accepts only a run on the release branch that tested the build's own commit.

## Reuse It for an Existing Build

A caller workflow in the same repository (or in a fork that hosts the same
build and evidence workflows) can call it without duplicating the runner:

{% raw %}

```yaml
name: verify-existing-build
on:
  workflow_dispatch:
    inputs:
      build_tag:
        description: Build run ID and attempt, e.g. 123456789-1
        required: true
        type: string

permissions:
  actions: read
  contents: read

jobs:
  evidence:
    uses: ./.github/workflows/evidence.yaml
    with:
      build_tag: ${{ inputs.build_tag }}
```

{% endraw %}

This runs containers on the caller's runners. A fork's evidence runs belong to
that fork; only runs on the branch that built the release, in the releasing
repository, can be release evidence.

The reusable interface takes **only `build_tag`**. It does not take an external
kit repository, revision or scenario as input, so do not copy this example into
an unrelated repository and claim it verifies that kit: external kits need a
dedicated, pinned, trusted-builder implementation first.

## Inputs, Outputs and Boundaries

- **Input:** `build_tag` has the form `<run_id>-<run_attempt>`. The matching
  `build-metadata-<build_tag>` artifact must be available in the repository.
- **What it tests:** the workflow checks out the build's `openadkit_sha` and
  takes the image digests from the same metadata, never latest aliases. It
  stages the kit with the same step that assembles release bundles, so the
  cells run the tree a release of that build ships, plus the example kit. The
  staged CLI's `openadkit new` makes that kit, with the fixture in
  `.github/scripts/evidence/kit` on top; its workspace builds against the
  build's `universe-common-devel` digest for each distro.
- **How it runs:** hosted runners execute the L0-L3 cells, retry a failed cell
  once, and aggregate every expected cell; a missing cell fails the run.
- **Output:** per-cell diagnostics and the `evidence-summary-<build_tag>`
  artifact, which the [release gate](../releases/evidence.md) reads.

Cells use `schemaVersion: 1`, and the summary (`schemaVersion: 3`) carries them
as written. Readers accept only these versioned payloads: a cell without
`schemaVersion: 1` and `metrics` is rejected. Read timings from `metrics`
rather than from top-level fields. Source and config checksums leave out the
`build`, `install` and `log` products of a workspace.
