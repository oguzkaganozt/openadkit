#!/usr/bin/env bash
# Dispatch a workflow on the current branch and wait until its run completes.
#
# usage: dispatch_and_wait.sh <workflow file> [input=value ...]
#
# With RUN_ID set, nothing is dispatched: that run is awaited instead. The run's
# id and attempt go to GITHUB_OUTPUT as run_id and run_attempt. Exits non-zero
# unless the run concludes with success; transient API failures are retried.
set -euo pipefail

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${GITHUB_REF_NAME:?GITHUB_REF_NAME is required}"
: "${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"
workflow=${1:?usage: dispatch_and_wait.sh <workflow file> [input=value ...]}
shift
poll_seconds=${POLL_SECONDS:-60}

run_id=${RUN_ID:-}
if [ -z "${run_id}" ]; then
  body=$(jq -n --arg ref "${GITHUB_REF_NAME}" '{ref: $ref, return_run_details: true, inputs: {}}')
  for pair in "$@"; do
    [[ "${pair}" == *=* ]] || { echo "Input '${pair}' is not name=value" >&2; exit 2; }
    body=$(jq --arg name "${pair%%=*}" --arg value "${pair#*=}" '.inputs[$name] = $value' <<<"${body}")
  done
  run_id=$(gh api -X POST "repos/${GITHUB_REPOSITORY}/actions/workflows/${workflow}/dispatches" \
    --input - --jq '.workflow_run_id' <<<"${body}")
fi
[[ "${run_id}" =~ ^[0-9]+$ ]] || { echo "No run id for ${workflow}: '${run_id}'" >&2; exit 1; }
echo "${workflow}: ${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY}/actions/runs/${run_id}"

while :; do
  if state=$(gh run view "${run_id}" -R "${GITHUB_REPOSITORY}" --json status,conclusion,attempt \
    --jq '"\(.status) \(.conclusion) \(.attempt)"' 2>/dev/null); then
    read -r status conclusion attempt <<<"${state}"
    if [ "${status}" = completed ]; then
      break
    fi
  fi
  sleep "${poll_seconds}"
done

{
  echo "run_id=${run_id}"
  echo "run_attempt=${attempt}"
} >>"${GITHUB_OUTPUT}"
echo "${workflow}: run ${run_id} attempt ${attempt} concluded ${conclusion}"
[ "${conclusion}" = success ]
