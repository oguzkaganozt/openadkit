"""Node lifecycle wiring without Docker/ROS runtime claims."""
import json
import os
import subprocess

import pytest
from release_fixtures import ROOT, executable


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
    result = subprocess.run(["bash", str(ROOT / ".github/scripts/evidence/run_cell.sh"), "planning-simulation", "humble", str(out), node],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=20)
    assert (result.returncode == 0) is (not failure), result.stderr
    report = json.loads((out / "cell.json").read_text())
    assert report["result"] == ("FAILED" if failure else "PASSED")
    assert report["build_tag"] == "123-1" and report["node"] == node
    recorded = [json.loads(line) for line in calls.read_text().splitlines()]
    def target(args):
        return args[args.index("--node") + 1] if "--node" in args else ""
    nodes = ["autoware", "scenario"] if node == "split" else [node]
    for operation in ("validate", "run", "stop"):
        expected = [] if operation == "run" and failure == "validate" else list(reversed(nodes)) if operation == "stop" else nodes
        assert [target(args) for args, _, _ in recorded if args[0] == operation] == expected
    if node == "split" and failure == "run":
        assert [(listen, peer) for args, listen, peer in recorded if args[0] == "run"] == [
            ("tcp/127.0.0.1:7447", env.get("ZENOH_PEER")), ("tcp/127.0.0.1:7448", "tcp/127.0.0.1:7447")]
