"""Quarantine classification does not turn a failed claim into PASSED."""

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence import test_result  # noqa: E402

TODAY = date(2026, 10, 1)


@pytest.mark.parametrize(("status", "expires", "expected", "passed", "warned", "failed", "expired"), [
    ("PASSED", None, "PASSED", ["flaky-cell"], [], [], None),
    ("FAILED", None, "FAILED", [], [], ["flaky-cell"], None),
    ("FAILED", "2026-11-01", "WARNED", [], ["flaky-cell"], [], False),
    ("FAILED", "2026-09-01", "FAILED", [], [], ["flaky-cell"], True),
    ("PASSED", "2026-11-01", "PASSED", ["flaky-cell"], [], [], None),
])
def test_classification(status, expires, expected, passed, warned, failed, expired):
    quarantine = [{"cell": "flaky-*", "reason": "known flake", "expires": expires}] if expires else []
    result = test_result.classify_cells([{"name": "flaky-cell", "result": status}], quarantine, TODAY)
    assert result[:4] == (expected, passed, warned, failed)
    assert result[4] == ([] if expired is None else [{
        "cell": "flaky-cell", "reason": "known flake", "expires": expires, "expired": expired,
    }])


def test_real_failure_beats_quarantined_failure():
    cells = [{"name": name, "result": "FAILED"} for name in ("flaky-cell", "solid-cell")]
    quarantine = [{"cell": "flaky-*", "reason": "known flake", "expires": "2026-11-01"}]
    assert test_result.classify_cells(cells, quarantine, TODAY)[:4] == ("FAILED", [], ["flaky-cell"], ["solid-cell"])


def test_quarantine_is_optional_but_invalid_expiry_fails(tmp_path):
    path = tmp_path / "quarantine.json"
    assert test_result.load_quarantine(path) == test_result.load_quarantine(None) == []
    path.write_text('{"quarantine":[{"cell":"x","reason":"why","expires":"soon"}]}')
    with pytest.raises(SystemExit, match="YYYY-MM-DD"):
        test_result.load_quarantine(path)


@pytest.mark.parametrize("include", [False, True])
def test_expected_names_match_workflow_matrix(include):
    matrix = [{"deployment": "planning-simulation", "distro": "humble"},
              {"deployment": "scenario-simulation", "distro": "jazzy", "node": "split"},
              {"deployment": "scenario-simulation", "distro": "humble", "node": None}]
    assert test_result.expected_cell_names({"include": matrix} if include else matrix) == [
        "planning-simulation-humble-linux-amd64", "scenario-simulation-jazzy-split-linux-amd64",
        "scenario-simulation-humble-linux-amd64",
    ]
    assert test_result.expected_cell_names({"include": []} if include else []) == []
