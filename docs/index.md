# Introduction

Open AD Kit adopts a modular, component-based architecture designed for flexibility, scalability, and platform independence. It leverages cloud-native principles and containerization to decompose [Autoware](https://github.com/autowarefoundation/autoware) into a collection of interoperable components. This approach allows developers to create customized autonomous driving (AD) systems by combining components to meet their specific needs.

## Architecture

The Autoware Foundation is a voting member of the [SOAFEE (Scalable Open Architecture For the Embedded Edge)](https://soafee.io/) initiative, and the **Autoware Open AD Kit is the first SOAFEE blueprint for the software-defined vehicle ecosystem**.

![Soafee Architecture](assets/images/openadkit.drawio.png)

## Deployments

A **deployment** is a running instance of Open AD Kit, a specific combination of **Autoware components** configured to achieve a particular task, such as a simulation or a full autonomous driving stack.

Deployments are defined using container orchestration files (e.g., `docker-compose.yaml`). This makes them portable and easy to reproduce across different environments, from a developer's laptop to edge devices in a vehicle. This container-based approach is a cornerstone of the Open AD Kit's cloud-native and platform-agnostic philosophy, aligning with standards like SOAFEE.

This modular structure allows users to start with a minimal deployment and incrementally add components as their system evolves.

For more details, see the [Deployments](./deployments/index.md).

## Components

The core functional components of the Open AD Kit are derived from the main **[Autoware](https://github.com/autowarefoundation/autoware)** project. Each image packages a focused part of the autonomous driving pipeline, which makes it possible to compose different AD systems from a common container set.

The primary images include:

- **Sensing and Perception**: Collects and processes sensor data.
- **Localization and Mapping**: Manages maps and vehicle pose estimation.
- **Planning and Control**: Produces and follows the driving trajectory.
- **Vehicle and System**: Packages vehicle interfaces and system-level services in the `vehicle-system` image.
- **API**: Offers an interface for external systems to interact with the vehicle.
- **Simulator**: Allows testing the AD stack in a virtual environment.
- **Visualizer**: Provides a browser-accessible RViz environment for remote inspection.

These images communicate through ROS 2 middleware, and some deployments bridge isolated environments with Zenoh. For more details, see the [Autoware components](./components/index.md).

## Key Features

### Modular Components

Open AD Kit is a microservice-based project designed to run on a variety of platforms. Each component is independent and can be deployed independently.

- **Independent images** for sensing, perception, mapping, localization, planning, control, APIs, simulation, and visualization
- **Multi-platform deployment** supporting both amd64 and arm64 architectures
- **Configurable ROS 2 container deployments** with environment-driven composition

![Granular Components](assets/images/granular-components.png)

### Mixed Criticality

Open AD Kit supports mixed-criticality deployment, enabling separation of safety-critical and non-critical components. This architecture allows flexible deployment strategies where critical autonomous driving functions can run on certified hardware while monitoring and development components operate on standard platforms.

- **Flexible deployment** separating safety-critical and monitoring components
- **Configurable criticality** from development testing to production safety systems
- **Hardware abstraction** supporting safety-island compute architectures

![Mixed Criticality](assets/images/mixed-criticality.png)

### Cloud Native

Open AD Kit leverages modern cloud-native technologies to deliver a scalable, portable AD stack.

- **Seamless scaling** from development laptops to production edge devices
- **Hybrid cloud support** bridging development and production environments
- **Containerized runtimes** using Docker Compose, Docker Bake, and platform-specific integrations such as AutoSD

![Cloud Native](assets/images/cloud-native.png)

### Connected and Continuous

Open AD Kit envisions an always-connected, complete autonomous driving development and deployment platform spanning data collection, calibration, and map annotation to machine learning operations, open-source simulation, and system validation.

- **Automated CI/CD** with GitHub Actions integration
- **Optimized build caching** for faster deployment cycles
- **Continuous testing** in containerized environments

![Connected and Continuous](assets/images/connected-continuous.png)

## Supported Platforms

Open AD Kit currently documents Ubuntu as the primary development host and AutoSD as the platform-specific deployment path available in this repository. EWAOL is planned but does not yet ship runnable assets here.

### Development Platforms

- Ubuntu 22.04, 24.04

### Platform-specific deployment paths

- [AutoSD](./platforms/autosd/index.md)
- [EWAOL](./platforms/ewaol/index.md) (planned)

For more details, see the [Supported SOAFEE Platforms](./platforms/index.md).

## Supported Hardware

For detailed information on system requirements, tested hardware, and cloud instances, please refer to the [Hardware](./hardware/index.md) section.
