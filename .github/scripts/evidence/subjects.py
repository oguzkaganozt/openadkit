"""Compute the evidence subject set from build metadata and the source tree.

Subjects are the built image digests plus the deployment and shared asset
checksums. The evidence workflow attests to this set and the release gate
recomputes it independently from the release tree.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from images import image_ref  # noqa: E402
from validation_matrix import (  # noqa: E402
    example_kit_checksums,
    kit_inventory,
    load_runtime,
)


def build_subjects(metadata: dict, source_root: Path):
    subjects: list[tuple[str, str]] = []
    build_tag = metadata.get("build_tag", "unknown")
    for image in metadata.get("images", []):
        digest = image.get("digest", "")
        if isinstance(digest, str) and digest.startswith("sha256:"):
            subjects.append(
                (
                    digest.removeprefix("sha256:"),
                    image_ref(image, build_tag),
                )
            )

    # The same inventory the release bundle is planned, staged and verified by.
    runtime = load_runtime(source_root)
    inventory = kit_inventory(runtime, source_root)
    for name, meta in inventory["deployments"].items():
        subjects.append((meta["checksum"], f"deployment:{name}"))
    for name, checksum in inventory["shared"].items():
        subjects.append((checksum, f"shared:{name}"))
    # Pin the integrator's source/config, not host-specific colcon products.
    # Recomputed by the release gate from the same source checkout.
    for path, checksum in example_kit_checksums(runtime, source_root).items():
        subjects.append((checksum, f"overlay:{path}"))

    subjects.sort(key=lambda item: item[1])
    return subjects


def write_subjects(path: Path, subjects) -> None:
    path.write_text(
        "".join(f"{digest}  {name}\n" for digest, name in subjects), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-metadata", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    metadata = json.loads(Path(args.build_metadata).read_text(encoding="utf-8"))
    subjects = build_subjects(metadata, Path(args.source_root).resolve())
    write_subjects(Path(args.output), subjects)
    print(json.dumps({"subjects": len(subjects)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
