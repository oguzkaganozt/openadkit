# CI ownership

The pipeline is **build → scan + runtime evidence → validate → package → publish**.
Workflows own triggers, job ordering, runners and permissions. Scripts own the
data and behavior contracts; local actions own repeated execution recipes.

| Responsibility | Owner |
| --- | --- |
| Build matrices, changed-target selection, contexts and Bake overrides | `scripts/build.py` |
| CI image tags, Bake execution and ccache restore/save/prune | `actions/build-image/` |
| Source lock import, Buildx and registry login | `actions/setup-build-env/` |
| Image metadata capture, inventory coverage, scan rows and artifact validation | `scripts/images.py` |
| Validation and evidence cell plans (roles, checks) and the kit inventory | `scripts/validation_matrix.py` |
| Executing one evidence cell: validate/start/cleanup and the L0–L3 checks it names | `scripts/evidence/run_cell.sh` |
| Cell payloads, the run summary and its report | `scripts/evidence/` |
| External release checks and sequencing | `scripts/validate_release.sh` |
| Immutable release plan, runtime pins, and bundle staging and integrity | `scripts/release_plan.py` |
| Packaging, image promotion and GitHub publication | `scripts/*release*.sh` |

The shared build action never grants permissions. A pull request from this
repository pushes the images it builds to the CI package `openadkit-ci`;
`scripts/assemble_pr_build.sh` completes that build there with the base
branch's other images, copied by digest, and `images.py capture` writes its
metadata, so `evidence.yaml` runs on it unchanged before merge. A fork's pull
request loads its images (no push, read-only token) and stops at the scan,
which applies the release gate's policy. Only pipeline changes (`PIPELINE_INPUTS`
in `build.py`) build a single image, `api`, which proves the pipeline end to end.
Temporary shared caches stay restricted to same-repository PRs. Published
builds retain exact upstream contexts, source/lock labels, security-refresh
stamps and the existing bounded cache policy. The local Bake graph in
`components/docker-bake.hcl` still owns Dockerfiles and dependency edges.

`images.py` keeps the existing unversioned, snake-case build/scan JSON formats.
It records **observed** registry platforms, not the inventory's expected list.
The scanner and release validator use the same digest/platform records; the
validator still checks raw-byte sidecar hashes and exact inventory coverage.
Shell retains the registry retry/error policy and GitHub run selection.

Shared parsing is **not** shared authorization: release validation still requires
the latest eligible full scan to pass and a successful evidence run whose summary
passed the promoted build. Packaging reparses image records and rechecks that
summary against the build and commit. Registry preflight remains at
both validation and promotion.

Release packaging and evidence staging assemble the kit through one
`release_plan.py --stage` step, so evidence runs the tree the release ships;
evidence adds only the example kits. The bundle, the release plan and the
evidence subjects all read one kit inventory.

Each evidence matrix row is the complete cell plan: identity, the role list in
manifest order and the deployment's verify step. L1 is `openadkit run`, which
waits for the deployment's healthchecks; L2 is `run --verify`; L3 is the example
kit's `checks/dev_loop.sh`. `run_cell.sh` executes the row with a common
validate/start/cleanup lifecycle; it does not derive policy from deployment
names. Scenario isolation and drive-to-goal checks stay distinct. Hosted split
evidence is two roles on one runner, not proof of two physical hosts.

The integrator example is made in CI, not kept in `deployments/`: the staged
CLI's `openadkit new example-kit` makes it under `kits/`, and the fixture in
`.github/scripts/evidence/kit/` adds every extension point on top. Lint
validates the same kit made from the checkout.

`registry-cleanup.yaml` deletes a pull request's CI images when it closes, CI
images after 14 days, branch builds after 90 days (the age a release may still
promote), the compile bases of builds older than that, the caches of images and
branches that no longer exist, and overwritten caches; release tags, latest
aliases and the moving `<target>-<arch>-<distro>` tags stay. Its weekly run
only lists until the repository variable `REGISTRY_CLEANUP` is `delete`.
`GITHUB_TOKEN` deletes
only in packages that give the repository the **Admin** role under the
package's *Manage Actions access*: set it on `openadkit`, `openadkit-buildcache`
and `openadkit-ci` in every repository that builds.

After changing a shared build owner, update both workflow path triggers and the
changed-input patterns in `build.py`. Python helpers needed by release and scan
must also be included in their trusted policy sparse checkouts.

Production docs builds record their checkout SHA in `openadkit-docs-source.txt`.
Inside the shared `gh-pages` publishing lane, `deploy-docs.yaml` rejects sources
older than, or divergent from, that published revision. Rebuilding the same SHA
is allowed. Before the first marked publication, the current default-branch head
is the baseline. A marker that is absent from the repository, such as one
inherited with a fork's `gh-pages`, is not comparable and also uses the
default-branch head as the baseline. PR previews do not replace the production
marker.
