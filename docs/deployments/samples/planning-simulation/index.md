# Planning Simulation

!!! abstract ""
    The Planning Simulation sample demonstrates the Open AD Kit planning simulation workflow. It runs the Autoware planning and control stack against a pre-recorded point cloud map, allowing you to set a goal pose and observe the vehicle plan and follow a trajectory in a virtual environment.

## What You Will See

After starting the deployment, you will access a noVNC-based RViz visualizer in your browser. From there you can:

- Set an initial pose for the ego vehicle
- Set a goal pose on the map
- Observe the planned trajectory, behavior planning, and control outputs in real time
- Monitor the vehicle as it follows the planned path

## Requirements

- Docker Engine
- Open AD Kit repository cloned and environment set up
- Planning simulation sample map (downloaded below)

!!! tip "GPU"
    A GPU is optional for this sample. The planning and control components run efficiently on CPU.

## Before You Start

### Download the Sample Map

The planning simulation requires a sample map. You can download it automatically with `gdown`:

```bash
# Install prerequisites if needed
sudo apt-get install -y python3-pip unzip
python3 -m pip install --user gdown

# Download and extract the sample map
mkdir -p ~/autoware_map
gdown -O ~/autoware_map/sample-map-planning.zip 'https://docs.google.com/uc?export=download&id=1499_nsbUbIeturZaDj7jhUownh5fvXHd'
unzip -o -d ~/autoware_map ~/autoware_map/sample-map-planning.zip
```

!!! info "About this map"
    This sample map (Copyright 2020 TIER IV, Inc.) is provided for demonstration purposes only. For production use, follow the [Autoware map creation guide](https://autowarefoundation.github.io/autoware-documentation/main/how-to-guides/integrating-autoware/creating-maps/).

## Start the Deployment

Navigate to the deployment directory and start the containers:

```bash
cd deployments/samples/planning-simulation
docker compose --env-file planning-simulation.env up -d
```

Wait approximately 10 seconds for the containers to initialize.

## Access the Visualizer

Open your browser and navigate to:

```
http://localhost:6080/vnc.html
```

Use the default password **`openadkit`** to access the visualizer. The RViz interface may take a few additional seconds to fully load.

!!! tip "Remote Access"
    If running on a remote server, replace `localhost` with the server's IP address:
    ```
    http://<your-server-ip>:6080/vnc.html
    ```

## Run the Simulation

Once the visualizer is open, follow the [Autoware planning simulation instructions](https://autowarefoundation.github.io/autoware-documentation/main/demos/planning-sim/lane-driving/#2-set-an-initial-pose-for-the-ego-vehicle) to:

1. Set an **initial pose** for the ego vehicle
2. Set a **goal pose** on the map
3. Observe the vehicle autonomously plan and execute the route

## Stop the Deployment

```bash
docker compose --env-file planning-simulation.env down
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Blank visualizer screen | Wait 10-30 seconds for containers to fully initialize, then refresh the browser |
| `file not found` error | Ensure the sample map was downloaded and extracted to `~/autoware_map` |
| Port 6080 in use | Modify the port mapping in `docker-compose.yaml` (e.g., `8080:6080`) |
| Vehicle does not move after setting goal | Check that the initial pose is set correctly and the map is loaded in RViz |

## Related

- [Scenario Simulation](../scenario-simulation/index.md) — Test with predefined traffic scenarios
- [Logging Simulation](../logging-simulation/index.md) — Replay recorded sensor data
- [Components Overview](../../../components/index.md) — Learn about the planning and control stack

<!-- DIAGRAM PLACEHOLDER:
     Description: Planning Simulation Architecture diagram
     Style: Single-machine container layout showing: planning-control container, visualizer container, shared map volume
     Blue-green accent on the planning-control component
     Dimensions: 800x300px, SVG preferred
-->
