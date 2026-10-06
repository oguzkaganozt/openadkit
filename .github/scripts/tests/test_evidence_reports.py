import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".github/scripts"))
from evidence.report import render  # noqa: E402


def test_legacy_summary_remains_readable_and_missing_metrics_are_not_zero():
    summary = {"result": "PASSED", "cells": [{"name": "one", "result": "PASSED", "ready_s": 12}]}
    text = render(summary)
    assert "Passing cells: **1/1**" in text
    assert "| PASSED | 12 | - | - |" in text
    assert "comparison" not in text


def test_comparison_is_explicit_and_uses_the_same_canonical_metrics():
    current = {"result": "PASSED", "cells": [{
        "schemaVersion": 1, "name": "one", "result": "PASSED",
        "metrics": {"ready_s": 12, "arrival_s": None, "peak_mib": 200},
    }]}
    previous = {"build_tag": "previous-build", "cells": [{"name": "one", "ready_s": 10, "peak_mib": 150}]}
    text = render(current, previous)
    assert "Metrics comparison vs build `previous-build`" in text
    assert "| one | ready_s | 10 | 12 | 2 |" in text
    assert "| one | arrival_s | - | - | - |" in text
    assert "not an upgrade acceptance test" in text


def test_diagnostic_report_keeps_quarantine_and_missing_cells_visible():
    current = {"result": "WARNED", "cells": [], "missing": ["absent"], "quarantine": [{
        "cell": "flaky", "expires": "2026-10-10", "expired": False, "reason": "tracked issue",
    }]}
    text = render(current)
    assert "flaky (quarantined, expires 2026-10-10): tracked issue" in text
    assert "Missing cell: absent" in text
