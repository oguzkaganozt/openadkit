# Samples

Sample deployments are self-contained configurations designed for **learning, development, and local testing**. Each sample demonstrates a specific Autoware workflow and can be started on a single machine with minimal setup.

## Available Samples

<div class="oak-card-grid">

<div class="oak-card">
<span class="oak-card-icon">:material-map-marker-path:</span>
<h3>Planning Simulation</h3>
<p>Run the Autoware planning stack against a pre-recorded point cloud map. Set a goal pose and watch the vehicle plan and follow a trajectory in a virtual environment.</p>
<p><span class="oak-badge oak-badge--verified">Single Machine</span> <span class="oak-badge oak-badge--supported">GPU Optional</span></p>
<a href="planning-simulation/" class="md-button">Run Planning Simulation</a>
</div>

<div class="oak-card">
<span class="oak-card-icon">:material-file-document-outline:</span>
<h3>Scenario Simulation</h3>
<p>Execute predefined traffic scenarios using the official TIER IV Scenario Simulator container. Validate planning and behavior under specific conditions.</p>
<p><span class="oak-badge oak-badge--verified">Single Machine</span> <span class="oak-badge oak-badge--supported">GPU Optional</span></p>
<a href="scenario-simulation/" class="md-button">Run Scenario Simulation</a>
</div>

<div class="oak-card">
<span class="oak-card-icon">:material-play-circle-outline:</span>
<h3>Logging Simulation</h3>
<p>Replay recorded sensor data (rosbag) through the full Autoware stack. Test perception, localization, and planning against real-world logged data.</p>
<p><span class="oak-badge oak-badge--verified">Single Machine</span> <span class="oak-badge oak-badge--testing">GPU Recommended</span></p>
<a href="logging-simulation/" class="md-button">Run Logging Simulation</a>
</div>

</div>

## Before You Start

All sample deployments require:

1. **Docker Engine** installed and running
2. **NVIDIA Container Toolkit** (optional but recommended for GPU acceleration)
3. **Open AD Kit repository cloned** and environment set up via `setup.sh`

!!! tip "GPU Recommendation"
    While planning and scenario simulations can run on CPU-only machines, the logging simulation benefits significantly from a GPU for sensing and perception tasks.

## Common Workflow

<div class="oak-steps">

- **Download assets** — Maps, rosbags, or artifacts as required by the specific sample
- **Configure environment** — Edit the `.env` file for your setup
- **Start the deployment** — Run `docker compose --env-file <sample>.env up -d`
- **Open the visualizer** — Access RViz via noVNC at `http://localhost:6080/vnc.html`
- **Interact with the simulation** — Set poses, launch scenarios, or play rosbags
- **Stop the deployment** — Run `docker compose --env-file <sample>.env down`

</div>

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Visualizer shows blank screen | Containers still initializing | Wait 10-30 seconds and refresh |
| `file not found` on startup | Map or rosbag not downloaded | Follow the asset download steps in the sample guide |
| Port already in use | Another service on 6080 | Change the port mapping in `docker-compose.yaml` |
| Poor performance | No GPU acceleration | Install NVIDIA Container Toolkit or reduce workload |

<!-- DIAGRAM PLACEHOLDER:
     Description: Sample Deployment Lifecycle diagram
     Style: Circular or horizontal flow showing: Download → Configure → Start → Visualize → Interact → Stop
     Use minimal icons, clean arrows, blue-green accent on the active step highlight
     Dimensions: 900x200px, SVG preferred
-->
