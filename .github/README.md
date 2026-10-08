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
| Runtime validation/start/cleanup and L0–L2 behavior checks | `scripts/evidence/run_cell.sh` |
| Signed cell payloads and evidence authorization | `scripts/evidence/` |
| External release checks and sequencing | `scripts/validate_release.sh` |
| Immutable release plan, runtime pins and bundle integrity | `scripts/release_plan.py` |
| Packaging, image promotion and GitHub publication | `scripts/*release*.sh` |

The shared build action never grants permissions. PR builds remain local
(`load`, no push), with temporary shared caches restricted to same-repository
PRs. Published builds retain exact upstream contexts, source/lock labels,
security-refresh stamps and the existing bounded cache policy. The local Bake
graph in `components/docker-bake.hcl` still owns Dockerfiles and dependency edges.

`images.py` keeps the existing unversioned, snake-case build/scan JSON formats.
It records **observed** registry platforms, not the inventory's expected list.
The scanner and release validator use the same digest/platform records; the
validator still checks raw-byte sidecar hashes and exact inventory coverage.
Shell retains the registry retry/error policy and GitHub run selection.

Shared parsing is **not** shared authorization: release validation still requires
the latest eligible full scan to pass and independently verifies the attestation
signature and one complete `PASSED` statement. Packaging reparses image records
and rechecks evidence against the promoted source. Registry preflight remains at
both validation and promotion, and sealed-plan hashes remain at publishing.

Single and split evidence cells resolve their node list once and use a common
validate/start/cleanup lifecycle. Scenario isolation and golden-path checks stay
distinct. Hosted split evidence is two nodes on one runner, not proof of two
physical hosts.

After changing a shared build owner, update both workflow path triggers and the
changed-input patterns in `build.py`. Python helpers needed by release and scan
must also be included in their trusted policy sparse checkouts.
