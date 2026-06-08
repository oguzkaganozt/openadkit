# Visualizer

The `visualizer` image provides a browser-accessible RViz environment via noVNC, allowing remote inspection of Autoware topics and state. It is designed as a lightweight component that can be deployed alongside the core stack or on a separate machine for remote monitoring.

## Visualizer Settings

The following environment variables can be configured when launching the visualizer container:

| Variable | Default Value | Possible Values | Description |
|----------|---------------|-----------------|-------------|
| `RVIZ_CONFIG` | `/autoware/rviz/autoware.rviz` | Any valid path | The full path to the RViz configuration file inside the container |
| `REMOTE_DISPLAY` | `true` | `true`, `false` | **(Recommended)** Browser-based RViz display accessible from any device. Set to `false` to launch a local RViz2 display |
| `REMOTE_PASSWORD` | `openadkit` | Any string without special characters | Password for the remote display (only used when `REMOTE_DISPLAY=true`) |
