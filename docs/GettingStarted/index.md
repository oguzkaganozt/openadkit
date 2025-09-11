# Getting Started

## Prerequisites

- Docker Engine
- Docker Compose
- NVIDIA Container Toolkit (Optional but highly recommended for sensing and perception tasks)
- Autoware artifacts (Optional but highly recommended for sensing and perception tasks)

    > All the above requirements can be installed by running the **setup.sh** script.

## Installation

1. Clone the repository

    ```bash
    git clone https://github.com/autowarefoundation/openadkit
    cd openadkit
    ```

2. Setup the runtime environment by running the following command, requires sudo privileges ( Skip if you already have the environment setup on your platform ):

    ```bash
    sudo ./setup.sh
    ```

    > You can use the `--no-nvidia` flag to skip the installation of the NVIDIA Container Toolkit if you don't have a **NVIDIA GPU**. Otherwise, it's **highly recommended** to install it to utilize CUDA for better performance for sensing and perception tasks.

3. Download the Autoware artifacts by running the following command, requires sudo privileges:

    ```bash
    sudo ./setup.sh --download-artifacts
    ```

## Running the Planning Simulation Deployment Sample

1. Run the following command to start the planning simulation deployment sample:

    ```bash
    docker compose -f deployments/samples/planning-simulation/docker-compose.yaml up -d
    ```

2. Visualize the simulation by accessing the following URL in your browser ( It can take a few seconds to visualizer to start ):

    ```bash
    http://localhost:6080/vnc.html
    ```

    Use the default password `openadkit` to access the visualizer.

    > If your machine is on a remote server, you can access the visualizer by using the following URL ( It can take a few seconds to visualizer to start ):
    >
    > ```bash
    > http://<your-server-public-ip>:6080/vnc.html
    > ```

3. Stop the planning simulation by running the following command:

    ```bash
    docker compose -f deployments/samples/planning-simulation/docker-compose.yaml down
    ```
