# Scenario Simulation

!!! abstract ""
    The Scenario Simulation sample runs the Autoware stack alongside the official [TIER IV Scenario Simulator](https://github.com/tier4/scenario_simulator_v2) container. It enables you to execute predefined traffic scenarios to validate planning and behavior under specific conditions — ideal for CI pipelines and regression testing.

## What You Will See

After starting the deployment, the scenario simulator generates a virtual traffic environment around the ego vehicle. You can:

- Watch the ego vehicle navigate predefined scenarios in the noVNC visualizer
- Observe behavior planning decisions (lane changes, intersection handling, obstacle avoidance)
- Review simulation results and metrics after scenario completion
- Define and run your own custom scenarios

## Requirements

- Docker Engine
- Open AD Kit repository cloned and environment set up

!!! info "No Manual Map Download Required"
    The default `sample.yaml` scenario uses the **Kashiwanoha** map bundled inside the TIER IV scenario simulator image. On first startup, the `map-init` service automatically extracts this map to `~/autoware_map/kashiwanoha_map`. It re-extracts the map if required files are missing or the configured TIER IV image tag changes.

!!! warning "Use the Correct Map"
    Do **not** use the `sample-map-planning` map with this deployment. The Kashiwanoha map is required. Using a different map will cause `setMap() for invalid version map`, missing route/localization, and repeated MRM transitions.

## Configuration

Edit `scenario-simulation.env` to customize the deployment:

| Variable | Description | Default |
|----------|-------------|---------|
| `SCENARIO` | Scenario file path inside the container | (bundled sample) |
| `SCENARIO_HOST_DIR` | Host directory mounted at `/scenarios` | `./scenarios/` |
| `OUTPUT_HOST_PATH` | Host directory for simulation results | `./output/` |
| `OUTPUT_DIRECTORY` | Container path for simulation results | — |
| `SCENARIO_SIMULATOR_IMAGE` | TIER IV scenario simulator image tag | (pinned in `.env`) |
| `SCENARIO_READY_TIMEOUT` | Max seconds to wait for Autoware readiness | 120 |
| `AUTO_EXTRACT_MAP` | Extract Kashiwanoha map from simulator image | `true` |
| `MAP_PATH` | Host map directory mounted into containers | `~/autoware_map` |

### Custom Scenarios

To run your own scenario:

1. Place your scenario YAML files under the `SCENARIO_HOST_DIR` (default: `./scenarios/`)
2. Set the scenario path in the environment file:
   ```bash
   SCENARIO=/scenarios/my-scenario.yaml
   ```

3. Simulation results are saved to `OUTPUT_HOST_PATH` (default: `./output/`)

!!! tip "Custom Maps"
    Custom scenarios must use the Kashiwanoha map unless you also provide a matching host map. For a different map, set `AUTO_EXTRACT_MAP=false`, update `MAP_PATH`, `LANELET2_MAP_FILE`, and `POINTCLOUD_MAP_FILE`, and ensure the files exist under `MAP_PATH` before starting.

## Start the Deployment

```bash
cd deployments/samples/scenario-simulation
docker compose --env-file scenario-simulation.env up -d
```

Wait approximately **90 seconds** for Autoware and the scenario simulator to initialize. The scenario runner waits up to `SCENARIO_READY_TIMEOUT` seconds for required Autoware map and API endpoints before launching.

## Access the Visualizer

Open your browser and navigate to:

```
http://localhost:6080/vnc.html
```

Use the default password **`openadkit`**. If running on a remote server, use the server's IP address and ensure port `6080` is reachable:

```
http://<server-ip>:6080/vnc.html
```

## Stop the Deployment

```bash
docker compose --env-file scenario-simulation.env down
```

## Expected Behavior

- The `map-init` service extracts the Kashiwanoha map on first run
- Autoware containers initialize and wait for the map
- The scenario simulator container starts and waits for Autoware readiness
- Once ready, the scenario executes automatically
- Results are written to the configured output directory

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Scenario does not start | Check that `map-init` completed successfully (required files in `~/autoware_map`) |
| `setMap() for invalid version map` | You are using the wrong map. Ensure Kashiwanoha is extracted, not `sample-map-planning` |
| Visualizer blank | Wait up to 90 seconds for full initialization; containers depend on each other sequentially |
| Missing results | Verify `OUTPUT_HOST_PATH` exists and is writable |

## Related Documentation

- [Scenario test simulation](https://autowarefoundation.github.io/autoware-documentation/main/demos/scenario-simulation/scenario-simulator/scenario-test-simulation/) — Official Autoware scenario simulation guide
- [Planning Simulation](../planning-simulation/index.md) — Simpler single-map simulation
- [Logging Simulation](../logging-simulation/index.md) — Replay recorded sensor data

<!-- DIAGRAM PLACEHOLDER:
     Description: Scenario Simulation Architecture diagram
     Style: Single-machine layout showing: autoware containers, scenario_simulator container, map-init service, visualizer
     Highlight the scenario_simulator → autoware ROS 2 DDS connection with blue-green accent
     Dimensions: 800x350px, SVG preferred
-->
