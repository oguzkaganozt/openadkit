"""Complete signed-claim fixtures for the release policy and packaging tests."""

from pathlib import Path

from evidence import release_gate

ROOT = Path(__file__).resolve().parents[3]


def passing_statement(metadata, source_root=ROOT):
    cells = release_gate.expected_cells(source_root)
    return {
        "_type": "https://in-toto.io/Statement/v1", "predicateType": release_gate.PREDICATE_TYPE,
        "subject": [{"name": name, "digest": {"sha256": digest}} for digest, name in release_gate.build_subjects(metadata, source_root)],
        "predicate": {
            "result": "PASSED", "passedTests": sorted(cells), "warnedTests": [], "failedTests": [],
            "url": "https://github.com/example/repo/actions/runs/456",
            "configuration": [
                {"name": name, "annotations": {"openadkitCell": {
                    "schemaVersion": 1, "name": name, "deployment": cell["deployment"], "distro": cell["distro"],
                    "node": cell.get("node") or None, "kit": cell.get("kit") or None,
                    "platform": "linux/amd64", "build_tag": metadata["build_tag"],
                    "source_sha": metadata["openadkit_sha"], "result": "PASSED",
                    "levels": {"L0": {"ok": True}, "L1": {"ok": True}, "L2": {"ok": True}},
                    "overlayConformant": True, "metrics": {"ready_s": 26, "arrival_s": 35, "peak_mib": 2151},
                }}} for name, cell in sorted(cells.items())
            ],
        },
    }


def passing_report(metadata, source_root=ROOT):
    return release_gate.statement_report(passing_statement(metadata, source_root), metadata, source_root, "humble", "example/repo", "refs/heads/release/2.0")
