# ROS snapshot

The upstream Autoware images ship binaries compiled against the ROS packages of
one ROS sync, but `packages.ros.org` only serves the latest sync. A stage that
installs from it can run those binaries, and ours, against versions they were
never compiled with. `diagnostic_updater` 4.2.6 -> 4.2.7 changed the `Updater`
constructor and broke the Jazzy images that way.

`ros-snapshot.sh <date> --check` points the ROS apt source at that date's
snapshot on `snapshots.ros.org` and fails unless every installed ROS package is
the snapshot's version. The universe-common and CUDA stages run it before any
apt step, devel and runtime alike; the component images inherit the source.
Every stage therefore installs the exact ROS versions the upstream images were
built with, and an upstream image that does not match the snapshot cannot
build. The images carry the date as the `org.opencontainers.image.ros-snapshot`
label, and the release notes and BOM name it per distro.

The snapshot is signed by the vendored `ros-snapshots.asc` (ROS Snapshot
builder, `4B63CF8FDE49746E98FA01DDAD19BAB3CBF125EA`). Ubuntu sources stay
live: Ubuntu updates keep the ABI of a release stable, and security fixes keep
flowing.

## Changing the snapshot

The dates live in `components/docker-bake.hcl` (`ROS_SNAPSHOT_HUMBLE`,
`ROS_SNAPSHOT_JAZZY`) and belong to `UPSTREAM_TAG`; change them together. Pick,
from the dates listed on `snapshots.ros.org/<distro>/`, the snapshot whose
check passes against the new release's `core-devel` image:

```bash
docker run --rm -e ROS_DISTRO=jazzy -v "$PWD/components/shared/ros-snapshot:/s:ro" \
  --entrypoint bash ghcr.io/autowarefoundation/autoware:core-devel-jazzy-<tag> \
  -c 'bash /s/ros-snapshot.sh <YYYY-MM-DD> --check'
```

The key expires on 2027-06-01. Replace `ros-snapshots.asc` with the extended
key from `keyserver.ubuntu.com` before then.

## Linked libraries

Without a lock, the runtime images rely on the rosdep exec dependencies for
every package the compiled tree links against, as upstream Autoware does.
`../check-linked-libs.sh` proves it at the end of each runtime stage: it runs
`ldd` on every library and `ldd -r` on every executable under `/opt/autoware`,
and fails the build on a missing library or an undefined symbol. This also
covers the images CI evidence cannot run (GPU, CARLA). `dlopen`-ed plugins,
Python modules, and launch-time packages are left to the release evidence.
