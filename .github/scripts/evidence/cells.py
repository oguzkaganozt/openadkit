"""One versioned cell payload for runners, attestations and derived views.

Legacy unversioned runner/summary rows and Test Result annotations are read at
the boundary only. Reading a statement here does not verify its signature or
authorize release; those are independent responsibilities of the release gate.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 1
METRICS = ("ready_s", "arrival_s", "peak_mib")


def normalize_cell(cell: dict[str, Any]) -> dict[str, Any]:
    version = cell.get("schemaVersion", SCHEMA_VERSION)
    if type(version) is not int or version != SCHEMA_VERSION:
        raise ValueError(f"unsupported evidence cell schemaVersion: {version!r}")
    return {
        **cell,
        "schemaVersion": SCHEMA_VERSION,
        "node": cell.get("node") or None,
        "kit": cell.get("kit") or None,
        "metrics": cell.get("metrics", {name: cell.get(name) for name in METRICS}),
    }


def predicate_cells(predicate: dict[str, Any]) -> list[dict[str, Any]]:
    cells = []
    for entry in predicate["configuration"]:
        annotations = entry.get("annotations")
        if not isinstance(annotations, dict):
            raise ValueError(f"{entry['name']}: missing annotations")
        if "openadkitCell" in annotations:
            payload = annotations["openadkitCell"]
            if not isinstance(payload, dict) or "schemaVersion" not in payload:
                raise ValueError(f"{entry['name']}: invalid versioned cell payload")
            cell = normalize_cell(payload)
            if cell.get("name") != entry["name"]:
                raise ValueError("cell payload name differs from configuration")
        else:
            # Read existing signed records without rewriting or resigning them.
            levels = annotations.get("levels")
            if not isinstance(levels, dict):
                raise ValueError(f"{entry['name']}: L0-L2 must all pass")
            cell = normalize_cell({
                "name": entry["name"],
                "deployment": annotations.get("deployment"),
                "distro": annotations.get("rosDistro"),
                "node": annotations.get("node"), "kit": annotations.get("kit"),
                "platform": annotations.get("platform"),
                "build_tag": annotations.get("buildTag"),
                "source_sha": annotations.get("sourceSha"),
                "result": (
                    "PASSED" if entry["name"] in predicate.get("passedTests", [])
                    else "WARNED" if entry["name"] in predicate.get("warnedTests", [])
                    else "FAILED"
                ),
                "levels": {
                    name: {"ok": ok} for name, ok in levels.items()
                },
                "overlayConformant": annotations.get("overlayConformant"),
                "metrics": {
                    "ready_s": annotations.get("readyS"),
                    "arrival_s": annotations.get("arrivalS"),
                    "peak_mib": annotations.get("peakMib"),
                },
            })
        cells.append(cell)
    return sorted(cells, key=lambda cell: cell["name"])


def report_cells(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive release views from the original statement, never a second copy."""
    if "statement" in document:
        return predicate_cells(document["statement"]["predicate"])
    return sorted((normalize_cell(cell) for cell in document["cells"]), key=lambda cell: cell["name"])


def legacy_release_cells(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Only for rechecking persisted schema-v1 release reports."""
    return [{
        "name": cell["name"], "deployment": cell["deployment"], "distro": cell["distro"],
        "node": cell["node"] or "", "kit": cell["kit"] or "", "platform": cell["platform"],
        "result": cell["result"],
        "levels": {name: data.get("ok") is True for name, data in cell["levels"].items()},
        "overlayConformant": cell.get("overlayConformant"),
        **cell["metrics"],
    } for cell in cells]
