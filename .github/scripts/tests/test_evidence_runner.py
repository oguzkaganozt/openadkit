"""Node lifecycle wiring without Docker/ROS runtime claims."""
import json
import os
import subprocess
import sys

import pytest
import yaml
from release_fixtures import ROOT, executable

import validation_matrix

RUNNER = ROOT / ".github/scripts/evidence/run_cell.sh"


def matrix_cell(deployment, node=""):
    """The real evidence-matrix row the workflow hands to the runner."""
    runtime = validation_matrix.load_runtime(ROOT)
    cells = validation_matrix.evidence_cells(runtime, ROOT) + validation_matrix.example_kit_cells(runtime, ROOT)
    return next(cell for cell in cells if cell["deployment"] == deployment and cell["distro"] == "humble"
                and cell.get("node", "") == node)


def test_evidence_cells_carry_the_manifest_plan():
    split = matrix_cell("scenario-simulation", "split")
    nodes = json.loads((ROOT / "deployments/scenario-simulation/deployment.json").read_text())["nodes"]
    assert split["nodes"].split() == list(nodes) and split["l2"] == "scenario" and "/clock" in split["fresh"].split()
    kit = matrix_cell("custom-kit")
    assert kit["l2"] == "golden" and kit["l1"] == "custom-kit" and "/acme/probe" in kit["fresh"].split()
    assert matrix_cell("planning-simulation")["nodes"] == ""
    for cell in (split, kit):
        assert cell["name"] == validation_matrix.evidence_cell_name(cell)


def test_unexempt_deployment_without_an_l2_check_fails_enumeration(monkeypatch):
    monkeypatch.delitem(validation_matrix.BEHAVIOUR_CHECKS, "scenario-simulation")
    with pytest.raises(ValueError, match="scenario-simulation has no L2 evidence check"):
        validation_matrix.evidence_cells(validation_matrix.load_runtime(ROOT), ROOT)


@pytest.mark.parametrize(("node", "failure"), [("", ""), ("autoware", "validate"), ("split", "validate"), ("split", "run")])
def test_cell_lifecycle_keeps_node_order_failures_and_cleanup(tmp_path, node, failure):
    cli = tmp_path / "bin/openadkit"
    executable(cli, '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ['CALLS']).open('a') as log:
    log.write(json.dumps([args, os.getenv('ZENOH_LISTEN'), os.getenv('ZENOH_PEER')]) + '\\n')
if args[0] == 'validate': print(json.dumps({'overlayConformant': True, 'deployment': args[1]}))
sys.exit(1 if args[0] == os.environ['FAILURE'] else 0)
''')
    executable(tmp_path / "bin/docker", "#!/usr/bin/env bash\nexit 0\n")
    calls = tmp_path / "calls"
    out = tmp_path / "out"
    env = os.environ | {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "OPENADKIT_CLI": str(cli),
                        "CALLS": str(calls), "FAILURE": failure, "BUILD_TAG": "123-1", "SOURCE_SHA": "b" * 40}
    nodes = "autoware scenario" if node == "split" else ""
    cell = matrix_cell("planning-simulation") | {"node": node, "nodes": nodes}
    result = subprocess.run(["bash", str(RUNNER), json.dumps(cell), str(out)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=20)
    assert (result.returncode == 0) is (not failure), result.stderr
    report = json.loads((out / "cell.json").read_text())
    assert report["result"] == ("FAILED" if failure else "PASSED")
    assert report["build_tag"] == "123-1" and report["node"] == node and report["name"] == cell["name"]
    recorded = [json.loads(line) for line in calls.read_text().splitlines()]
    def target(args):
        return args[args.index("--node") + 1] if "--node" in args else ""
    nodes = ["autoware", "scenario"] if node == "split" else [node]
    for operation in ("validate", "run", "stop"):
        expected = [] if operation == "run" and failure == "validate" else list(reversed(nodes)) if operation == "stop" else nodes
        assert [target(args) for args, _, _ in recorded if args[0] == operation] == expected
    if node == "split":
        for operation in ("validate", "run"):
            if operation == "run" and failure == "validate":
                continue
            assert [(listen, peer) for args, listen, peer in recorded if args[0] == operation] == [
                ("tcp/127.0.0.1:7447", env.get("ZENOH_PEER")), ("tcp/127.0.0.1:7448", "tcp/127.0.0.1:7447")]


def test_split_l0_uses_real_manifest_endpoint_requirements(tmp_path):
    cli = tmp_path / "bin/openadkit"
    executable(cli, f'''#!{sys.executable}
import json, sys
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'cli')!r})
import manifest
args = sys.argv[1:]
if args[0] == 'validate':
    root = Path({str(ROOT)!r}); kit = manifest.load_kit(root)
    manifest.get_deployment(root, kit, args[1]).select(kit, 'humble', False, node=args[args.index('--node') + 1])
    print(json.dumps({{'overlayConformant': True}}))
sys.exit(1 if args[0] == 'run' else 0)
''')
    executable(tmp_path / "bin/docker", "#!/usr/bin/env bash\nexit 0\n")
    env = {k: v for k, v in os.environ.items() if k not in ("ZENOH_LISTEN", "ZENOH_PEER", "OPENADKIT_KIT")}
    env.update(PATH=f"{tmp_path / 'bin'}:{os.environ['PATH']}", OPENADKIT_CLI=str(cli),
               HOME=str(tmp_path), OPENADKIT_CONFIG_DIR=str(tmp_path / 'config'))
    subprocess.run(["bash", str(RUNNER), json.dumps(matrix_cell("scenario-simulation", "split")), str(tmp_path / "out")],
                   env=env, cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert json.loads((tmp_path / "out/cell.json").read_text())["levels"]["L0"]["ok"] is True


@pytest.mark.parametrize(("topics", "rc", "expected"), [("/clock", 0, "0"), ("/api/routing/state", 0, "1"), ("", 1, "failed"), ("", 124, "failed")])
def test_isolation_counts_zero_without_hiding_discovery_failure(tmp_path, topics, rc, expected):
    # Capture and execute the actual Docker probe command from the shell runner.
    executable(tmp_path / "bin/docker", '''#!/usr/bin/env python3
import os, subprocess, sys
if '--entrypoint' not in sys.argv: sys.exit(0)
command = sys.argv[sys.argv.index('-c') + 1]
command = command.replace('source "/opt/ros/${ROS_DISTRO}/setup.bash"', 'true')
sys.exit(subprocess.run(['bash', '-c', command]).returncode)
''')
    executable(tmp_path / "bin/ros2", f"#!/usr/bin/env bash\nprintf '%s\\n' {topics!r}\nexit {rc}\n")
    text = RUNNER.read_text()
    probe = text[text.index('isolation=$(\n'):text.index('\n                else', text.index('isolation=$(\n'))]
    env = os.environ | {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "ROS_DISTRO": "humble"}
    result = subprocess.run(["bash", "-c", 'distro=humble; image=test; ' + probe + '\nprintf "%s" "$isolation"'],
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0 and result.stdout == expected, result.stderr


def test_evidence_metadata_survives_checkout_and_cells_install_compose(tmp_path):
    jobs = yaml.safe_load((ROOT / ".github/workflows/evidence.yaml").read_text())["jobs"]
    steps = jobs["prepare"]["steps"]
    executable(tmp_path / "bin/gh", '''#!/usr/bin/env python3
import json, sys
from pathlib import Path
destination = Path(sys.argv[sys.argv.index('--dir') + 1])
(destination / 'build-metadata.json').write_text(json.dumps({'openadkit_sha': 'b' * 40}))
''')
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    env = os.environ | {"PATH": f"{tmp_path / 'bin'}:{os.environ['PATH']}", "RUNNER_TEMP": str(tmp_path / "runner"),
                        "GITHUB_EVENT_NAME": "workflow_dispatch", "DISPATCH_BUILD_TAG": "123-1",
                        "GITHUB_REPOSITORY": "example/repo", "GITHUB_OUTPUT": str(tmp_path / "outputs")}
    result = subprocess.run(["bash", "-c", steps[0]["run"]], cwd=workspace, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not list(workspace.iterdir())  # Nothing for checkout to remove.
    assert json.loads((tmp_path / "runner/openadkit-build-metadata/build-metadata.json").read_text())["openadkit_sha"] == "b" * 40
    assert '$RUNNER_TEMP/openadkit-build-metadata/build-metadata.json' in next(s["run"] for s in steps if s["name"] == "Stage evidence kit")
    assert next(s["with"]["path"] for s in steps if s["name"] == "Upload build metadata").startswith('${{ runner.temp }}')
    cell_steps = jobs["cell"]["steps"]
    install = next(i for i, s in enumerate(cell_steps) if s.get("run") == "bash .github/scripts/install-compose.sh")
    assert install < next(i for i, s in enumerate(cell_steps) if s["name"] == "Run evidence cell")


RUN = "[scenario_test_runner.py-1] Run sample_{i}.xosc (1 of 1)\n"
# The interpreter colors "Passed"; a colored verdict must still count.
PASSED = "[openscenario_interpreter_node-3] [INFO] [simulation.openscenario_interpreter]: \x1b[32mPassed\x1b[0m\n"


@pytest.mark.parametrize(("cases", "log", "ok"), [
    (['<testcase name="sample_0"/>', '<testcase name="sample_1"/>'], RUN.format(i=0) + PASSED + RUN.format(i=1) + PASSED, True),
    # One of two scenarios ran and passed: incomplete, not a pass.
    (['<testcase name="sample_0"/>', '<testcase name="sample_1"/>'], RUN.format(i=0) + PASSED, False),
    # A skipped case did not run.
    (['<testcase name="sample_0"><skipped/></testcase>'], RUN.format(i=0) + PASSED, False),
    (['<testcase name="sample_0"><failure/></testcase>'], RUN.format(i=0), False),
])
def test_scenario_metrics_pass_only_complete_runs(tmp_path, cases, log, ok):
    (tmp_path / "out").mkdir()
    (tmp_path / "out/result.junit.xml").write_text(f"<testsuites><testsuite>{''.join(cases)}</testsuite></testsuites>")
    (tmp_path / "scenario.log").write_text(log)
    result = subprocess.run([sys.executable, str(ROOT / ".github/scripts/evidence/scenario_metrics.py"),
                             "--output-dir", str(tmp_path / "out"), "--log", str(tmp_path / "scenario.log"),
                             "--json", str(tmp_path / "metrics.json")], capture_output=True, text=True)
    assert (result.returncode == 0) is ok, result.stdout
    assert json.loads((tmp_path / "metrics.json").read_text())["ok"] is ok


FAKE_ROS2 = """#!/usr/bin/env bash
# Lists every name; publishes on the topic only from the FRESH_AFTER-th echo.
case "$1 $2" in
  "service list"|"topic list") printf '%s\\n' /api/a /api/b ;;
  "topic echo")
    count=$(( $(cat "${ECHO_COUNT}" 2>/dev/null || echo 0) + 1 ))
    echo "${count}" > "${ECHO_COUNT}"
    [ "${count}" -ge "${FRESH_AFTER}" ] || exit 1
    echo "data: 1" ;;
esac
"""


@pytest.mark.parametrize(("fresh_after", "timeout", "ok", "echoes"), [
    # A topic that starts publishing late still passes within the deadline.
    (2, "60", True, 2),
    # Past the deadline, one window is all it gets.
    (99, "1", False, 1),
])
def test_readiness_waits_for_late_publishers_until_the_deadline(tmp_path, fresh_after, timeout, ok, echoes):
    executable(tmp_path / "ros2", FAKE_ROS2)
    env = os.environ | {"PATH": f"{tmp_path}:{os.environ['PATH']}", "ECHO_COUNT": str(tmp_path / "count"),
                        "FRESH_AFTER": str(fresh_after)}
    result = subprocess.run(
        [sys.executable, str(ROOT / ".github/scripts/evidence/readiness.py"), "--service", "/api/a",
         "--topic", "/api/b", "--fresh", "/api/b", "--timeout", timeout, "--fresh-timeout", "1",
         "--output", str(tmp_path / "readiness.json")],
        env=env, capture_output=True, text=True)
    assert (result.returncode == 0) is ok, result.stdout + result.stderr
    timeline = json.loads((tmp_path / "readiness.json").read_text())
    assert timeline["items"][-1]["ok"] is ok
    assert int((tmp_path / "count").read_text()) == echoes
