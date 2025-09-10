# Getting Started

## Prerequisites

- Docker Engine
- Docker Compose
- NVIDIA Container Toolkit (Optional but highly recommended)

    > All the above requirements can be installed by running the **setup.sh** script.

## Installation

1. Clone the repository

    ```bash
    git clone https://github.com/autowarefoundation/openadkit
    cd openadkit
    ```

2. Setup the environment by running the following command ( Skip if you already have the environment setup ):

    ```bash
    ./setup.sh
    ```

    > You can use the `--no-nvidia` flag to skip the installation of the NVIDIA Container Toolkit if you don't have a **NVIDIA GPU**. Otherwise, it's **highly recommended** to install it to utilize CUDA for better performance for sensing and perception tasks.

## Running the Local Planning Simulation Deployment Example

1. Run the following command to start the local planning simulation deployment example:

    ```bash
    docker compose -f deployments/generic/local-planning-simulation/docker-compose.yaml up -d
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

3. Stop the local planning simulation by running the following command:

    ```bash
    docker compose -f deployments/generic/local-planning-simulation/docker-compose.yaml down
    ```
