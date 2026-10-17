#!/usr/bin/env bash
# Emit the build-all-images workflow summary as Markdown.
set -euo pipefail

: "${BUILD_TAG:?BUILD_TAG is required}"
: "${AUTOWARE_INPUT_REF:?AUTOWARE_INPUT_REF is required}"
: "${AUTOWARE_REF_TYPE:?AUTOWARE_REF_TYPE is required}"
: "${AUTOWARE_REF:?AUTOWARE_REF is required}"
: "${AUTOWARE_BASE_VERSION:?AUTOWARE_BASE_VERSION is required}"
: "${SCAN_REQUESTED:?SCAN_REQUESTED is required}"
: "${SOURCE_REF:?SOURCE_REF is required}"

echo "## Build Complete"
echo "| Key | Value |"
echo "|-----|-------|"
echo "| **build_tag** | \`${BUILD_TAG}\` |"
echo "| **autoware_input_ref** | \`${AUTOWARE_INPUT_REF}\` |"
echo "| **autoware_ref_type** | \`${AUTOWARE_REF_TYPE}\` |"
echo "| **autoware_ref** | \`${AUTOWARE_REF}\` |"
echo "| **autoware_base_version** | \`${AUTOWARE_BASE_VERSION}\` |"
echo "| **scan_requested** | \`${SCAN_REQUESTED}\` |"
echo ""
echo "## Release Eligibility"

autoware_stable_re='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
release_line=$(printf '%s\n' "${SOURCE_REF}" | sed -nE 's#^refs/heads/release/((0|[1-9][0-9]*)\.(0|[1-9][0-9]*))$#\1#p')
if [ -n "${release_line}" ] && [ "${AUTOWARE_REF_TYPE}" = "tag" ] \
  && printf '%s\n' "${AUTOWARE_INPUT_REF}" | grep -Eq "${autoware_stable_re}"; then
  echo "This build can be released as an OpenADKit v${release_line}.Z version after a passed full scan."
  echo ""
  echo "On \`release/${release_line}\`, run **Actions -> scan-images** and **Actions -> evidence** with \`build_tag\` \`${BUILD_TAG}\`, then **Actions -> release** with the same \`build_tag\`."
else
  echo "This is a development build. Releases come from release/X.Y branches, whose \`.github/autoware.ref\` pins an Autoware X.Y.Z release."
fi
