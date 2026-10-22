#!/usr/bin/env bash
# Resolve shared build inputs for build-all-images and build-single-image.
# Writes GitHub Actions outputs directly to GITHUB_OUTPUT.
#
# .github/autoware.ref selects the Autoware sources: an exact release tag
# builds on that release's upstream images (release/X.Y); a commit of upstream
# main builds for upstream development from the dependency lock and upstream
# base image digests committed next to it, .github/autoware-lock.repos and
# .github/autoware-base-images.json (main, moved weekly by bump-autoware.yaml).
# A branch name still works for local experiments, resolved anew each build.
set -euo pipefail

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"
: "${GITHUB_RUN_ID:?GITHUB_RUN_ID is required}"
: "${GITHUB_RUN_ATTEMPT:?GITHUB_RUN_ATTEMPT is required}"
: "${GITHUB_EVENT_NAME:?GITHUB_EVENT_NAME is required}"

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=.github/scripts/registry_lookup.sh
# shellcheck disable=SC1091
source "${script_dir}/registry_lookup.sh"

autoware_input_ref=$(cat .github/autoware.ref)
[ -n "${autoware_input_ref}" ] || { echo "The Autoware pin is empty" >&2; exit 1; }
build_tag="${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
# Registry caches per branch, so development and release builds do not evict
# each other; pull requests read their base branch's.
cache_scope=$(printf '%s' "${GITHUB_BASE_REF:-${GITHUB_REF_NAME:?GITHUB_REF_NAME is required}}" | tr -c 'A-Za-z0-9_.-' '-')
# The weekly snapshot bump is main's next state: share main's caches, so its
# build recompiles only what the new snapshot changed.
[ "${cache_scope}" != ci-bump-autoware ] || cache_scope=main

scan_requested=false
if [ "${GITHUB_EVENT_NAME}" = "schedule" ]; then
  scan_requested=true
elif [ "${GITHUB_EVENT_NAME}" = "workflow_dispatch" ] && [ "${RUN_SCAN_INPUT:-false}" = "true" ]; then
  scan_requested=true
fi

git init autoware-metadata >&2
if git -C autoware-metadata remote get-url origin >/dev/null 2>&1; then
  git -C autoware-metadata remote set-url origin https://github.com/autowarefoundation/autoware
else
  git -C autoware-metadata remote add origin https://github.com/autowarefoundation/autoware
fi

fetch_ref="${autoware_input_ref}"
autoware_ref_type="ref"
if git -C autoware-metadata ls-remote --exit-code origin "refs/heads/${autoware_input_ref}" >/dev/null 2>&1; then
  fetch_ref="refs/heads/${autoware_input_ref}"
  autoware_ref_type="branch"
elif git -C autoware-metadata ls-remote --exit-code origin "refs/tags/${autoware_input_ref}" >/dev/null 2>&1; then
  fetch_ref="refs/tags/${autoware_input_ref}"
  autoware_ref_type="tag"
elif printf '%s\n' "${autoware_input_ref}" | grep -Eq '^[0-9a-fA-F]{40}$'; then
  autoware_ref_type="sha"
else
  alt_tag=""
  if printf '%s\n' "${autoware_input_ref}" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+'; then
    alt_tag="${autoware_input_ref#v}"
  elif printf '%s\n' "${autoware_input_ref}" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+'; then
    alt_tag="v${autoware_input_ref}"
  fi
  if [ -n "${alt_tag}" ] && git -C autoware-metadata ls-remote --exit-code origin "refs/tags/${alt_tag}" >/dev/null 2>&1; then
    fetch_ref="refs/tags/${alt_tag}"
    autoware_ref_type="tag"
  fi
fi

if [ "${autoware_ref_type}" = "ref" ]; then
  echo "Could not resolve '${autoware_input_ref}' as a branch, tag, or SHA in the Autoware repository" >&2
  exit 1
fi

# A branch name moves daily. A check of one change builds on the Autoware
# revision and dependency lock of REUSE_IMAGE, the base branch's published
# compile base, so its unchanged images stay reusable. Tags and commits are
# pinned already.
lock_build_tag=""
if [ "${autoware_ref_type}" = branch ] && [ -n "${REUSE_IMAGE:-}" ] \
  && labels=$(registry_inspect_json "${REUSE_IMAGE}" | jq -c '.image.config.Labels // {}'); then
  label() {
    jq -r --arg key "org.opencontainers.image.$1" '.[$key] // empty' <<<"${labels}"
  }
  if [ "$(label autoware-input-ref)" = "${autoware_input_ref}" ] \
    && [[ "$(label autoware-ref)" =~ ^[0-9a-f]{40}$ ]] && [[ "$(label build-tag)" =~ ^[0-9]+-[0-9]+$ ]]; then
    fetch_ref=$(label autoware-ref)
    lock_build_tag=$(label build-tag)
    echo "Building on the Autoware revision of ${REUSE_IMAGE} (build ${lock_build_tag})" >&2
  fi
fi

# Fetch the requested ref plus all tags so git describe can find the nearest semver tag.
# A single fetch keeps FETCH_HEAD pointed at the requested ref; a bare "git fetch --tags"
# would clobber FETCH_HEAD with the remote default branch and silently build from main.
git -C autoware-metadata fetch --filter=blob:none --tags --force origin "${fetch_ref}"
git -C autoware-metadata checkout --detach FETCH_HEAD

autoware_ref=$(git -C autoware-metadata rev-parse HEAD)
autoware_base_version=$(
  git -C autoware-metadata describe --tags --match 'v[0-9]*.[0-9]*.[0-9]*' --abbrev=0 2>/dev/null \
    || git -C autoware-metadata describe --tags --match '[0-9]*.[0-9]*.[0-9]*' --abbrev=0 2>/dev/null \
    || true
)
if printf '%s\n' "${autoware_input_ref}" | grep -Eq '^v?[0-9]+\.[0-9]+\.[0-9]+$'; then
  autoware_base_version="${autoware_input_ref#v}"
fi
[ -n "${autoware_base_version}" ] || {
  echo "Could not infer Autoware base version from ${autoware_input_ref}" >&2
  exit 1
}

# Release builds use that release's upstream images. Development builds
# compile core themselves, from the committed lock of a pinned commit, or
# from upstream's development manifest resolved now for a branch.
upstream_tag=""
autoware_overlay=autoware-metadata/repositories/autoware-nightly.repos
autoware_lock_file=""
upstream_pins=""
if [ "${autoware_ref_type}" = tag ]; then
  upstream_tag="${autoware_base_version}"
  autoware_overlay=""
  # A release line created from main inherits main's development snapshot.
  for snapshot_file in .github/autoware-lock.repos .github/autoware-base-images.json; do
    [ ! -f "${snapshot_file}" ] || {
      echo "A release pin builds on that release's own manifest and images; remove ${snapshot_file}" >&2
      exit 1
    }
  done
elif [ "${autoware_ref_type}" = sha ]; then
  autoware_lock_file=.github/autoware-lock.repos
  upstream_pins=.github/autoware-base-images.json
  autoware_overlay=""
  [ -f "${autoware_lock_file}" ] || {
    echo "An Autoware commit pin needs its dependency lock in ${autoware_lock_file}; run .github/scripts/bump_autoware.py" >&2
    exit 1
  }
  [ -f "${upstream_pins}" ] || {
    echo "An Autoware commit pin needs its base image digests in ${upstream_pins}; run .github/scripts/bump_autoware.py" >&2
    exit 1
  }
elif [ ! -f "${autoware_overlay}" ]; then
  echo "Development manifest not found: ${autoware_overlay}" >&2
  exit 1
fi

{
  echo "autoware_input_ref=${autoware_input_ref}"
  echo "autoware_ref_type=${autoware_ref_type}"
  echo "autoware_ref=${autoware_ref}"
  echo "autoware_base_version=${autoware_base_version}"
  echo "upstream_tag=${upstream_tag}"
  echo "autoware_overlay=${autoware_overlay}"
  echo "autoware_lock_file=${autoware_lock_file}"
  echo "upstream_pins=${upstream_pins}"
  echo "lock_build_tag=${lock_build_tag}"
  echo "cache_scope=${cache_scope}"
  echo "build_tag=${build_tag}"
  echo "scan_requested=${scan_requested}"
} >> "${GITHUB_OUTPUT}"
