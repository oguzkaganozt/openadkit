# Autoware Service-Based Deployment

This sample deployment shows how to run **service-based** autoware to demonstrate the **end-to-end functionality with granular services** using planning and logging simulations.

## Requirements

In order to run the service-based deployment with planning and logging simulations, you need to have the **sample maps** and **rosbag**. You can download them by running the following commands:

> **Note**: Skip this step if you already have the sample maps and rosbag from the [planning simulation](../planning-simulation/README.md) and [logging simulation](../logging-simulation/README.md) deployment samples.

### Sample Maps

Download and unpack sample maps using below commands:

1. Logging Simulation Map

    ```bash
    gdown -O ~/autoware_map/ 'https://docs.google.com/uc?export=download&id=1A-8BvYRX3DhSzkAnOcGWFw5T30xTlwZI'
    unzip -d ~/autoware_map/ ~/autoware_map/sample-map-rosbag.zip
    ```

    - You can also download [the logging simulation map](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view?usp=sharing) manually.

2. Planning Simulation Map

    ```bash
    gdown -O ~/autoware_map/ 'https://docs.google.com/uc?export=download&id=1499_nsbUbIeturZaDj7jhUownh5fvXHd'
    unzip -d ~/autoware_map ~/autoware_map/sample-map-planning.zip
    ```

    - You can also download [the planning simulation map](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view?usp=sharing) manually.

> **Note**: Sample maps(Copyright 2020 TIER IV, Inc.) are only for demonstration purposes. You can use your own map by following the [How-to Guide](https://autowarefoundation.github.io/autoware-documentation/main/how-to-guides/integrating-autoware/creating-maps/).

### Sample Rosbag

Download and unpack sample rosbag using below commands:

```bash
gdown -O ~/autoware_map/ 'https://docs.google.com/uc?export=download&id=1sU5wbxlXAfHIksuHjP3PyI2UVED8lZkP'
unzip -d ~/autoware_map/ ~/autoware_map/sample-rosbag.zip
```

- You can also download [the rosbag](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view?usp=sharing) manually.

> **Note**: Due to privacy concerns, the rosbag(Copyright 2020 TIER IV, Inc.) does not contain image data, which will cause: Traffic light recognition functionality cannot be tested with this sample rosbag. Object detection accuracy is decreased.

## Run the Deployment

### Planning Simulation

1. Start the deployment by running the following command:

    ```bash
    docker compose \
    --env-file planning-simulation.env \
    --profile planning-simulation --profile visualization up -d
    ```

2. Open a browser to visualize the simulation and navigate to:

    ```bash
    http://localhost:6080/vnc.html
    ```

    Use the default password `openadkit` to access the visualizer. **It can take a few seconds to visualizer to start.**

    > If your machine is on a remote server, you can access the visualizer by using its accessible IP address:
    >
    > ```bash
    > http://<your-server-ip>:6080/vnc.html
    > ```

3. After you see the visualizer, you can start the autonomous driving simulation by following the [planning simulation instructions](https://autowarefoundation.github.io/autoware-documentation/main/tutorials/ad-hoc-simulation/planning-simulation/#2-set-an-initial-pose-for-the-ego-vehicle) in the Autoware documentation.

4. Stop the deployment by running the following command:

    ```bash
    docker compose \
    --env-file planning-simulation.env \
    --profile planning-simulation --profile visualization down
    ```

### Logging Simulation

1. Start the deployment by running the following command:

    ```bash
    docker compose \
    --env-file logging-simulation.env --env-file logging-simulation.gpu.env \
    -f docker-compose.yaml -f docker-compose.gpu.yaml \
    --profile logging-simulation --profile visualization up -d
    ```

2. Open a browser to visualize the simulation and navigate to:

    ```bash
    http://localhost:6080/vnc.html
    ```

    Use the default password `openadkit` to access the visualizer. **It can take a few seconds to visualizer to start.**

    > If your machine is on a remote server, you can access the visualizer by using its accessible IP address:
    >
    > ```bash
    > http://<your-server-ip>:6080/vnc.html
    > ```

3. To start the logging simulation, you should run the following command to play the rosbag:

    ```bash
    docker compose --env-file logging-simulation.env -f docker-compose.yaml up rosbag -d
    ```

4. Stop the deployment by running the following command:

    ```bash
    docker compose \
    --env-file logging-simulation.env --env-file logging-simulation.gpu.env \
    -f docker-compose.yaml -f docker-compose.gpu.yaml \
    --profile logging-simulation --profile visualization --profile rosbag down
    ```
