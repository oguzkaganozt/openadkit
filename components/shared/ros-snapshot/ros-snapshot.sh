#!/usr/bin/env bash
set -euo pipefail

# Point the ROS apt source at a dated snapshot of packages.ros.org.
#
# packages.ros.org only serves the latest ROS sync, while the upstream Autoware
# images ship binaries compiled against the sync they were built from. Using
# that sync's snapshot keeps every stage on the exact ROS versions those
# binaries, and ours, link against. See README.md.
#
# Usage: ros-snapshot.sh <YYYY-MM-DD> [--check]
#   --check  fail unless every installed ROS package is the snapshot's version

snapshot="${1:?usage: ros-snapshot.sh <YYYY-MM-DD> [--check]}"
check="${2:-}"
: "${ROS_DISTRO:?ROS_DISTRO is required}"
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=/dev/null
. /etc/os-release

# Replace the live ROS source: ros2-apt-source links ros2.sources, older images
# carry a .list entry.
grep -l 'packages\.ros\.org' /etc/apt/sources.list.d/* 2>/dev/null | xargs -r rm -f
[ ! -f /etc/apt/sources.list ] || sed -i '/packages\.ros\.org/d' /etc/apt/sources.list
# Key 4B63CF8FDE49746E98FA01DDAD19BAB3CBF125EA (ROS Snapshot builder).
install -m 0644 "${script_dir}/ros-snapshots.asc" /usr/share/keyrings/ros-snapshots.asc
cat > /etc/apt/sources.list.d/ros2-snapshot.sources <<EOF
Types: deb
URIs: http://snapshots.ros.org/${ROS_DISTRO}/${snapshot}/ubuntu
Suites: ${VERSION_CODENAME}
Components: main
Signed-By: /usr/share/keyrings/ros-snapshots.asc
EOF
apt-get update

[ "${check}" = --check ] || exit 0

mapfile -t installed < <(
    dpkg-query -W -f='${db:Status-Abbrev} ${Package}=${Version}\n' "ros-${ROS_DISTRO}-*" |
        awk '$1 == "ii" { print $2 }' | sort
)
[ "${#installed[@]}" -gt 0 ] || { echo "ros snapshot: no ROS packages installed" >&2; exit 1; }
# Installed versions the snapshot does not serve.
mismatched=$(comm -23 <(printf '%s\n' "${installed[@]}") <(
    apt-cache madison "${installed[@]%%=*}" |
        awk -F'|' '{ gsub(/ /, "", $1); gsub(/ /, "", $2); print $1 "=" $2 }' | sort -u
))
if [ -n "${mismatched}" ]; then
    echo "ros snapshot ${snapshot} does not match this image's ROS packages:" >&2
    printf '%s\n' "${mismatched}" | head -20 | sed 's/^/  /' >&2
    echo "Set the ROS snapshot the upstream image was built from (components/docker-bake.hcl)." >&2
    exit 1
fi
echo "ros snapshot ${snapshot}: ${#installed[@]} installed ROS packages match"
