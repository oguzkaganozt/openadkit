# Hardware

What a host needs to run Open AD Kit, and the boards with their own support.

## Host Requirements

For deployments, simulation and development:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 8 cores | 16 cores |
| RAM | 16 GB | 32 GB |
| GPU | None | NVIDIA with 2 GB+ VRAM for Planning Simulation's GPU mode, 4 GB+ for Logging Simulation's; 16 GB for CARLA Simulation |
| Storage | 50 GB | 100 GB+ SSD |

Images are published for **amd64** and **arm64**. The GPU modes and CARLA
Simulation are amd64-only: the CUDA images do not fall back to CPU, so hosts
without an NVIDIA GPU, and all arm64 hosts, run the CPU images.

On a host below the recommended size Autoware may not keep up in real time;
Scenario Simulation can then run slower than real time with
[`GLOBAL_REAL_TIME_FACTOR`](../deployments/scenario-simulation.md#configure).

## Boards

| Board | Architecture | Support |
|-------|--------------|---------|
| R-Car X5H | arm64 | AutoSD 10 image in [openadkit-rcar-x5h](https://github.com/autowarefoundation/openadkit-rcar-x5h), its own repository; board tests are manual |

No board is part of the release evidence: the
[evidence cells](../releases/evidence.md) run on hosted amd64 runners, and
native arm64 cells are planned.
