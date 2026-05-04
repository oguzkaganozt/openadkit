# Autoware Open AD Kit CARLA Simulation

This sample deployment shows how to run Autoware Open AD Kit with CARLA as an external simulator.

## Requirements

- Docker Compose (v2)
- A CARLA simulation-capable host and Docker image access
- Optional GPU support for CARLA rendering

## Run the deployment

1. Start services:

   ```bash
   docker compose --env-file carla-simulation.env up -d
   ```

2. Open RViz at:

   ```bash
   http://localhost:6080/vnc.html
   ```

   Password: `openadkit`

3. Set initial pose in RViz and run your standard planning simulation scenario.

## Stop the deployment

```bash
docker compose --env-file carla-simulation.env down
```
