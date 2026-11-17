# Findings of the Pre-Release Review

Open findings from five independent reviews of v2.0.0-rc.10 (new-user journey, CLI code, kit authoring, release pipeline, deployments), checked against the code. The fixes that were small and clear landed in #147. Each item names where it is, what goes wrong and a suggested fix.

**Plan:** before 2.0, the items marked *before 2.0*; CARLA (5) with a hand test on a GPU host; the rest as upstream issues grouped by area.

## A. Release Pipeline

- **1. The bundle is packaged by the release branch's scripts, not the tested commit's.** *Before 2.0, small.*
  - Where: `package_release_bundles.sh:16` runs `release_plan.py`, `validation_matrix.py`, `images.py` and `autoware_patches.py` from `workflow_sha`; `stage_kit.sh:31` stages the evidence kit with the build commit's copies. `CI.md` says evidence runs the tree the release ships.
  - Impact: a packaging change that does not fail (image mapping, runtime file list, inventory) ships a bundle no evidence ran. One that fails blocks promoting an older build: after #146, build `44061434662-1` can no longer be packaged.
  - Fix: fail validation when those scripts differ between `release_sha` and `workflow_sha`, or package with `release_sha`'s scripts.

- **2. Evidence is tied to the build tag and commit, not to image digests.** *Issue, medium.*
  - Where: `evidence_is_release` (`validate_release.sh`) checks tag and SHA only; the scan is tied by digest (`images.py`).
  - Impact: re-running one job of a successful build pushes new images under the same tag and re-uploads `build-metadata-<tag>`. A release dispatched after the new scan passes, while the new evidence still runs, ships new digests with old evidence. `container-images.md` says a CI build tag does not move.
  - Fix: put a sha256 of `build-metadata.json` in `evidence-summary.json` and require it to match.

- **3. Repository settings do not enforce what `release-process.md` says.** *Issue, upstream admin.*
  - Upstream `release` environment: no deployment-branch policy, `prevent_self_review: false`.
  - No ruleset protects `release/*`, although each `release/X.Y` branch runs its own gate scripts and `verification.md` accepts `refs/heads/release/X.Y`.
  - `RELEASE_TOKEN` is a repository secret, not an environment secret; `release.yaml` exposes it as `GH_TOKEN` to every publish step, third-party actions included.
  - Tag creation is not restricted by ruleset.
  - Fix: restrict the environment to `main` and `release/*`, prevent self-review, move the token into the environment and set it only on the steps that run `gh`, protect `release/*` like `main`.

- **4. Supply chain gaps.** *Issue.*
  - No scan age limit: the gate accepts a build's latest scan however old (up to 90 days); the weekly scan covers only `main`'s latest build.
  - `setup-buildx-action` uses the latest buildx and the floating `moby/buildkit:buildx-stable-1` builder for release builds.
  - `components/simulator/Dockerfile:122-123` pip-installs `transforms3d` with no version or hash.
  - `create-manifest.sh` drops BuildKit provenance and nothing signs or attests the images.
  - `install-compose.sh` downloads its checksum from the same release as the binary.
  - `lint.yaml` installs pip and npm tools and actionlint unpinned (pull requests only, read-only token).
  - Nits: `promote_release_images.sh:12-13` says the workflow checks the plan's digest, nothing does; `release_evidence` is worked out twice with different rules (`evidence.yaml:145`, `summary.py:74`); `scan-images.yaml:149-165` repeats the Trivy step to retry it; `resolve_build_inputs.sh:22` maps `/` to `-`, so `release-2.0` shares `release/2.0`'s cache scope.

## B. CARLA Simulation

- **5. `carla-interface` gets none of the shared Autoware service setup.** *Before 2.0 if hand-tested, medium.*
  - Where: `deployments/carla-simulation/compose.carla.yaml:51-77`.
  - Impact: no healthcheck and no `/openadkit/config` or overlay mounts. When the bridge node dies (for example on a CARLA RPC timeout) `ros2 launch` keeps running, the container stays up, and `run` and `status` look fine while Autoware gets no sensors or clock. `restart` never selects it, and a kit override of `autoware_carla_interface` only produces "package is in no service".
  - Fix: `extends: {file: ../shared/services/autoware.yaml, service: autoware}` and drop the keys that duplicates. Needs a CARLA run on a GPU host; CI has none.

## C. Deployments

- **6. Logging Simulation has the shortest wait budget.** *Before 2.0, one line.* `deployments/logging-simulation/deployment.json` sets no `waitTimeout`, so it gets 300 s; it is the heaviest CPU stack, the others get 480-600 s. Fix: `"waitTimeout": 600`.

- **7. Wrong comments and a missing `init`.** *Before 2.0, small.*
  - `deployments/carla-simulation/compose.yaml:9-10` says Compose replaces `depends_on` on merge; Compose takes the union, so the edges restated for `vehicle` and `sensing` are redundant.
  - `compose.zenoh.yaml:33-35` (both deployments) says `ZENOH_*` comes from `settings.env`; no `settings.env` defines them.
  - The Zenoh bridge is the only service without `init: true`.

- **8. Simplifications.** *Issue.*
  - `deployments/safety-island-simulation/compose.yaml:7-56` is byte-identical to `deployments/planning-simulation/compose.yaml:7-56`; a topology fix to one misses the other. Include Planning's file and add the Safety Island services.
  - `depends_on: - map` is redundant on every service with `pid: service:map`, and the short form drops the `restart: true` Compose adds for that dependency, so services that join map's namespace behave differently.
  - `deployments/shared/services/perception.yaml:14` mounts the whole data directory read-write into perception, maps, rosbags and the Safety Island binary included. Check whether the model engine cache needs write access before narrowing it.

- **9. Already tracked upstream:** GPU wiring done two ways (#208); settings files that hold internal wiring, `CARLA_WORLD_PORT` and CARLA's dead `ROS_DISTRO=humble` (#214).

## D. Usability

- **10. `logs --follow` prints the whole history before it streams.** *Before 2.0, small.* `cli/live.py` passes no `--tail`; a planning-simulation up for 4 hours held about 43,000 log lines. Fix: `--tail N`, about 100 by default with `--follow`.

- **11. Errors without a next step.** *Before 2.0, small.*
  - `NVIDIA Container Toolkit is unavailable for the selected GPU mode` (`cli/compose.py`): add "run: openadkit setup --gpu".
  - `setup --gpu` without a driver fails with `nvidia-smi is unavailable` (`cli/setup.sh`): add "install the NVIDIA driver first".

- **12. `uninstall` is silent about the Docker images.** *Before 2.0, small.* Each image is 5.5-6 GB and `planning-cuda` is 17 GB; `cli.md` and the final message mention only the data, and `uninstall --help` says to run `clean` first while the docs do not. Fix: print and document the image removal step and "clean first".

- **13. The Scenario Simulation page understates the wait and never says how to read the result.** *Before 2.0, docs.* `scenario-simulation.md:18-20` says about 90 seconds; `INITIALIZE_DURATION=300`, and evidence shows 101-131 s to ready, then 425-501 s for the scenario. Point to `run --verify` and the `scenario: N of M passed` line.

- **14. For a newcomer.** *Issue.*
  - `status` never names the deployment, distro or GPU mode, although the run record holds them.
  - `planning-simulation.md` lists no services; `status` shows nine.
  - Until an initial pose is set the logs fill with expected warnings (`Subscribed control_cmd is timed out`, diagnostics timeouts); nothing says this is normal.
  - The engage step is worded four ways (README, Quickstart, CARLA, Safety Island).
  - The linked Autoware guide's fallback uses `source ~/autoware/install/setup.bash`; give the `openadkit shell api ros2 service call ...` equivalent.
  - Help nits: the top-level help prints the command list twice and its examples omit `status` and `logs`; `openadkit --version` is unrecognized; `version` prints Autoware twice; `validate --data` prints its error before the report in pipes; `data.py:108` prints raw byte counts; `--ros-distro` help lists no values; `uninstall --help` names the internal Compose project prefix.

## E. Kits

- **15. `kit-guide.md:228-230` misdescribes `acme-probe`.** *Before 2.0, one sentence.* It says the service mounts `${OPENADKIT_OVERLAY_WS}` itself; it gets the mount through `extends: autoware.yaml`, and its only own volume is `../../checks`.

- **16. Documentation gaps.** *Issue.*
  - No documented way to drop a base service in a single-host base. `profiles: ["off"]` on the service in the kit's `compose.yaml` works.
  - Extra services on a non-Open-AD-Kit ROS image have no recipe: the docs never say the stack runs on ROS domain 1, and the `ota-agent` example has no host network or `runtime.env`. Say "extend `autoware.yaml`", or give the `network_mode`, `env_file` and `cyclonedds.xml` lines.
  - `new-vehicle.md:14-17` says to copy the four `sample_*` packages without saying from where or at which Autoware ref; line 47 says to find parameter files in the images with no recipe (`docker run --rm <image> find /opt/autoware/share -name ...`).
  - The kit docs tell authors to set `LANELET2_MAP_FILE`, `POINTCLOUD_MAP_FILE` and `SCENARIO_HOST_PATH`, which the stable list in `releases/compatibility.md` does not cover.
  - `cli/templates/kit/README.md:16-17` lists the host settings file as a layer for config overrides; it holds settings only.

- **17. Silent mistakes.** *Issue.*
  - `openadkit build ./my-kit` fails with "has no src/ to build"; `run` and `validate` accept the kit root. Treat a kit root as its `overlay_ws`.
  - `config/<package>/...` without the `autoware/` level is skipped by the CLI and `overlay.py`, and a copied `deployments/<name>/deployment.json` is ignored, both without a warning. Extend `warn_unread_kit_files`.
  - A symlink to the user's own complete data (`maps -> /mnt/ssd/maps`) is reported as incomplete (`cli/data.py:45-48`), and the advice deletes the link and downloads into the home directory. Treat a symlink to an unmarked, non-empty directory as the user's own, or say symlinked data is unsupported.
  - Two deployments of one kit can claim one data destination; kit-wide `validate` could reject it. `clean`'s "also used by" note looks only at the release's deployments.
  - `validate` and `run` help offer `--role` to kits, which have no roles.

## F. CLI Internals

- **18. Small bugs.** *Issue.*
  - `cli/setup.sh:6`: `TARGET_USER=${SUDO_USER:-...}`; under `sudo -u alice` the invoking admin joins the docker group instead of alice. Use `$(id -un)`.
  - `cli/main.py:97-111` with `templates/kit/openadkit.json`: the `extends` path is inserted into JSON as raw text, so a path with `"` or `\` makes an invalid manifest. Use `json.dumps`.
  - `cli/main.py:315`: on a source checkout without git, `version` fails with `[Errno 2] ... 'git'` instead of `commit: unknown`.
  - `openadkit:308` against `cli/catalog.py:65`: Python expands `~` and `$HOME` in `OPENADKIT_HOME`, the launcher does not, so a kit's automatic install fails with `OPENADKIT_HOME='~/oak'`; the message also blames `OPENADKIT_HOME` when `XDG_DATA_HOME` is the relative one.
  - `openadkit:237-238`: two kit commands auto-installing the same pinned release at once; the second fails. Accept a release that appeared complete.

- **19. Duplication.** *Issue.*
  - "The pinned release is installed" is checked in three places (`cli/main.py:132`, `:154`, `cli/catalog.py:478`) and differently in the launcher (`openadkit:121`, which also needs an executable launcher). Use one helper.
  - Two `UsageError` classes (`cli/main.py:47`, `cli/installation.py:55`).
  - `cli/data.py:397-403` is unreachable (`validate_install_targets` raises first) and prints a literal `<deployment>`.
  - In `run_command`, a local `report` shadows the module-level `report()`.
