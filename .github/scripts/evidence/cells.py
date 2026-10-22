"""One versioned cell payload for runners, attestations and derived views.

Reading a statement here does not verify its signature or authorize release;
those are independent responsibilities of the release gate.
"""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 1
METRICS = ("ready_s", "arrival_s", "peak_mib")


def normalize_cell(cell: dict[str, Any]) -> dict[str, Any]:
    version = cell.get("schemaVersion")
    if type(version) is not int or version != SCHEMA_VERSION:
        raise ValueError(f"unsupported evidence cell schemaVersion: {version!r}")
    if not isinstance(cell.get("metrics"), dict):
        raise ValueError(f"{cell.get('name')}: missing cell metrics")
    return {**cell, "node": cell.get("node") or None, "kit": cell.get("kit") or None}


def predicate_cells(predicate: dict[str, Any]) -> list[dict[str, Any]]:
    cells = []
    for entry in predicate["configuration"]:
        annotations = entry.get("annotations")
        if not isinstance(annotations, dict):
            raise ValueError(f"{entry['name']}: missing annotations")
        payload = annotations.get("openadkitCell")
        if not isinstance(payload, dict):
            raise ValueError(f"{entry['name']}: invalid versioned cell payload")
        cell = normalize_cell(payload)
        if cell.get("name") != entry["name"]:
            raise ValueError("cell payload name differs from configuration")
        cells.append(cell)
    return sorted(cells, key=lambda cell: cell["name"])


def report_cells(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive release views from the original statement, never a second copy."""
    if "statement" in document:
        return predicate_cells(document["statement"]["predicate"])
    return sorted((normalize_cell(cell) for cell in document["cells"]), key=lambda cell: cell["name"])
