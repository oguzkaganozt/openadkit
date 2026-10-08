#!/usr/bin/env python3
"""Plan CI builds: inventory matrices, changed targets and the shared Bake recipe.

Prints `KEY=<compact-json>` lines for each matrix to stdout. The `prepare`
job redirects this into `$GITHUB_OUTPUT`. Uses only the standard library so
it runs before any pip/apt install step.
"""
import fnmatch
import json
import os
import pathlib
import sys

DEFAULT_INVENTORY = ".github/image-inventory.json"


def platform_label(platform):
    if platform == "linux/amd64":
        return "amd64"
    if platform == "linux/arm64":
        return "arm64"
    raise ValueError(f"unsupported platform: {platform}")


def image_distros(image, default_distros):
    return image.get("ros_distros", default_distros)


def build_matrices(inventory):
    distros = inventory["ros_distros"]
    images = inventory["images"]

    def matrix_for(stage, include_target=None, exclude_targets=None):
        exclude_targets = set(exclude_targets or [])
        include = []
        for image in images:
            if image["stage"] != stage:
                continue
            if include_target is not None and image["target"] != include_target:
                continue
            if image["target"] in exclude_targets:
                continue
            for distro in image_distros(image, distros):
                for platform in image["platforms"]:
                    include.append({
                        "platform": platform,
                        "platform-label": platform_label(platform),
                        "ros-distro": distro,
                        "target": image["target"],
                    })
        return {"include": include}

    common_pairs = sorted({
        (platform, distro)
        for image in images if image["stage"] == "common"
        for distro in image_distros(image, distros)
        for platform in image["platforms"]
    })
    common_matrix = {"include": [
        {"platform": p, "platform-label": platform_label(p), "ros-distro": d}
        for p, d in common_pairs
    ]}

    manifest_include = []
    for image in images:
        arches = " ".join(platform_label(p) for p in image["platforms"])
        for distro in image_distros(image, distros):
            manifest_include.append({
                "repo": image["repo"],
                "target": image["target"],
                "ros-distro": distro,
                "arches": arches,
            })
    manifest_matrix = {"include": manifest_include}

    return {
        "common_matrix": common_matrix,
        "component_matrix": matrix_for("component", exclude_targets={"carla-interface"}),
        "carla_matrix": matrix_for("component", include_target="carla-interface"),
        "manifest_matrix": manifest_matrix,
    }


def build_single_image_plan(inventory, changed_files=(), target_input="", distro="humble"):
    images = inventory["images"]
    images_by_target = {image["target"]: image for image in images}
    all_targets = set(images_by_target)
    shared_build_inputs = (
        "components/runtime-cleanup.sh",
        "components/link-lock/*",
        "components/overlay/*",
        "components/security-refresh.sh",
        ".github/image-inventory.json",
        ".github/scripts/export_autoware_lock.py",
        ".github/scripts/build.py",
        ".github/scripts/resolve_build_inputs.sh",
        ".github/scripts/resolve_registry_contexts.sh",
        ".github/scripts/resolve_upstream_images.sh",
        ".github/scripts/registry_lookup.sh",
        ".github/actions/free-disk-space/*",
        ".github/actions/build-image/*",
        ".github/actions/setup-build-env/*",
        ".github/workflows/build-single-image.yaml",
        ".trivyignore",
    )
    targets = set(target_input.split())
    use_local_common = False
    use_local_simulator = False

    if not target_input:
        for changed_file in changed_files:
            if not changed_file:
                continue
            if changed_file == "components/docker-bake.hcl":
                targets.update(all_targets)
                use_local_common = True
                use_local_simulator = True
            elif changed_file == "components/README.md" or fnmatch.fnmatchcase(
                changed_file, "components/*/README.md"
            ):
                continue
            elif any(
                fnmatch.fnmatchcase(changed_file, pattern)
                for pattern in shared_build_inputs
            ):
                targets.update(all_targets)
            elif changed_file.startswith("components/"):
                component, separator, component_path = changed_file.removeprefix(
                    "components/"
                ).partition("/")
                if component == "sensing-perception" and separator:
                    if component_path == "Dockerfile":
                        mapped_targets = {"sensing-perception"}
                    elif component_path == "Dockerfile.cuda":
                        mapped_targets = {"sensing-perception-cuda"}
                    else:
                        mapped_targets = {
                            "sensing-perception",
                            "sensing-perception-cuda",
                        }
                elif component == "universe-common" and separator:
                    mapped_targets = all_targets
                elif component == "simulator" and separator:
                    mapped_targets = {"simulator", "carla-interface"}
                elif component in images_by_target and separator:
                    mapped_targets = {component}
                else:
                    mapped_targets = None

                if mapped_targets is None:
                    raise ValueError(f"Unmapped component build input: {changed_file}")
                targets.update(mapped_targets)
                use_local_common |= component == "universe-common"
                use_local_simulator |= component == "simulator"

    if use_local_simulator and "carla-interface" in targets:
        targets.discard("simulator")

    unknown_targets = targets - all_targets
    if unknown_targets:
        raise ValueError(f"Unknown Bake target: {sorted(unknown_targets)[0]}")

    distro = distro or "humble"
    if distro not in inventory["ros_distros"]:
        raise ValueError(f"Unsupported ROS distro: {distro}")

    for target in sorted(targets):
        supported_distros = image_distros(
            images_by_target[target], inventory["ros_distros"]
        )
        if distro not in supported_distros:
            supported = ", ".join(supported_distros)
            raise ValueError(
                f"Target '{target}' does not support ROS distro '{distro}' "
                f"(supported: {supported})"
            )

    return {
        "targets_json": sorted(targets),
        "setup_autoware": any(target != "carla-interface" for target in targets),
        "with_middleware": bool(
            targets & {"universe-common-devel", "universe-common"}
        ),
        "use_local_common": use_local_common,
        "use_local_simulator": use_local_simulator,
    }


def format_outputs(matrices):
    lines = [f"{k}={json.dumps(v, separators=(',', ':'))}" for k, v in matrices.items()]
    return "\n".join(lines) + "\n"


def bake_recipe(inventory, prepared, target, distro, platform, *, publish, shared_common, common_cached, owner, source_sha, run_id):
    """Overlay the local HCL graph, preserving local dependency builds in PRs."""
    images = {image["target"]: image for image in inventory["images"]}
    if target not in images or distro not in image_distros(images[target], inventory["ros_distros"]) or platform not in images[target]["platforms"]:
        raise ValueError(f"Unsupported build cell: {target}/{distro}/{platform}")
    arch = platform_label(platform)
    build_tag = prepared["build_tag"]
    cache = f"ghcr.io/{owner}/openadkit-buildcache:{target}-{arch}-{distro}-main"
    contexts = {}
    args = {"ROS_DISTRO": distro}
    labels = {}
    cache_from = [f"type=registry,ref={cache}"]
    cuda_contexts = {}
    if publish:
        if target == "universe-common":
            upstream = json.loads(prepared["upstream_images"])[distro]
            contexts.update({f"autoware-{name}": upstream[name]["uri"] for name in ("core-devel", "base")})
            args["SECURITY_REFRESH"] = build_tag
        else:
            common = f"ghcr.io/{owner}/openadkit-common"
            contexts.update({name: f"docker-image://{common}:{name}-{arch}-{distro}-{build_tag}" for name in ("universe-common-devel", "universe-common")})
            if target != "carla-interface":
                upstream = json.loads(prepared["upstream_images"])[distro]
                cuda_contexts = {f"autoware-{name}": upstream[name]["uri"] for name in ("base-cuda-runtime", "base-cuda-devel")}
        if target == "carla-interface":
            contexts["simulator"] = f"docker-image://ghcr.io/{owner}/openadkit:simulator-amd64-{distro}-{build_tag}"
        else:
            args["ROS_ALIGN_STAMP"] = build_tag
        labels = {f"org.opencontainers.image.{key.replace('_', '-')}": prepared[key] for key in (
            "autoware_input_ref", "autoware_ref_type", "autoware_ref", "autoware_base_version", "autoware_lock_sha256",
        )}
        labels.update({"org.opencontainers.image.build-tag": build_tag, "org.opencontainers.image.run-id": run_id,
                       "org.opencontainers.image.openadkit-sha": source_sha})
        # Match the existing Bake --set label spelling; context readers accept
        # these legacy quoted keys as well as canonical OCI keys.
        labels = {f'"{key}"': value for key, value in labels.items()}
    else:
        for key, name in (("upstream_core_devel", "autoware-core-devel"), ("upstream_base", "autoware-base"),
                          ("devel_context", "universe-common-devel"), ("runtime_context", "universe-common")):
            if prepared.get(key) and not (shared_common and name.startswith("universe-common")):
                contexts[name] = prepared[key]
        for key, name in (("upstream_cuda_runtime", "autoware-base-cuda-runtime"), ("upstream_cuda_devel", "autoware-base-cuda-devel")):
            if prepared.get(key) and not shared_common:
                cuda_contexts[name] = prepared[key]
        if target == "carla-interface" and prepared.get("use_local_simulator") != "true":
            contexts["simulator"] = prepared["simulator_context"]
        if not shared_common:
            if prepared.get("use_local_common") == "true":
                cache_from.append(f"type=registry,ref=ghcr.io/{owner}/openadkit-buildcache:universe-common-{arch}-{distro}-main")
            if common_cached:
                cache_from.extend(f"type=gha,scope=pr-common-{stage}-{run_id}" for stage in ("devel", "runtime"))
            if prepared.get("use_local_simulator") == "true":
                cache_from.append(f"type=registry,ref=ghcr.io/{owner}/openadkit-buildcache:simulator-{arch}-{distro}-main")

    # Apply the same settings to dependency targets too, as the previous *.set
    # overrides did. HCL remains the owner of Dockerfiles and local graph edges.
    overrides = {}
    for name in images:
        overrides[name] = {"platforms": [platform], "args": args.copy(), "labels": labels.copy(),
                           "contexts": contexts.copy(), "cache-from": cache_from.copy()}
        if publish:
            overrides[name]["cache-to"] = [f"type=registry,ref={cache},mode=max"]
    overrides["sensing-perception-cuda"]["contexts"].update(cuda_contexts)
    if publish and target not in ("universe-common", "carla-interface"):
        overrides["sensing-perception-cuda"]["args"]["SECURITY_REFRESH"] = build_tag
    if shared_common:
        for name, stage in (("universe-common-devel", "devel"), ("universe-common", "runtime")):
            overrides[name]["cache-to"] = [f"type=gha,scope=pr-common-{stage}-{run_id},mode=min"]
    targets = ["universe-common-devel", "universe-common"] if publish and target == "universe-common" else [target]
    return {"target": overrides}, targets


def write_recipe():
    inventory = json.loads(pathlib.Path(DEFAULT_INVENTORY).read_text())
    target = os.environ["BUILD_TARGET"]
    distro = os.environ["ROS_DISTRO"]
    platform = os.environ["BUILD_PLATFORM"]
    recipe, targets = bake_recipe(
        inventory, json.loads(os.environ["BUILD_INPUTS"]), target, distro, platform,
        publish=os.environ["PUBLISH"] == "true", shared_common=os.environ["SHARED_COMMON"] == "true",
        common_cached=os.environ["COMMON_CACHED"] == "true", owner=os.environ["GITHUB_REPOSITORY"].split("/")[0],
        source_sha=os.environ["GITHUB_SHA"], run_id=os.environ["GITHUB_RUN_ID"],
    )
    pathlib.Path(".build-recipe.json").write_text(json.dumps(recipe))
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"cache_prefix=buildkit-mounts-{target}-{distro}-{platform_label(platform)}-\n")
        output.write("targets<<BUILD_TARGETS\n" + "\n".join(targets) + "\nBUILD_TARGETS\n")


def main(argv):
    if len(argv) > 1 and argv[1] == "recipe":
        write_recipe()
        return 0
    if len(argv) > 1 and argv[1] == "single-image":
        if len(argv) != 4:
            print("usage: build.py single-image ROS_DISTRO TARGETS", file=sys.stderr)
            return 2
        inventory = json.loads(pathlib.Path(DEFAULT_INVENTORY).read_text())
        try:
            plan = build_single_image_plan(
                inventory,
                changed_files=sys.stdin.read().splitlines(),
                target_input=argv[3],
                distro=argv[2],
            )
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        sys.stdout.write(format_outputs(plan))
        targets = " ".join(plan["targets_json"])
        print(f"Detected targets: '{targets}'", file=sys.stderr)
        return 0

    path = argv[1] if len(argv) > 1 else DEFAULT_INVENTORY
    inventory = json.loads(pathlib.Path(path).read_text())
    sys.stdout.write(format_outputs(build_matrices(inventory)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
