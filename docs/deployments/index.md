# Deployments

A running instance of an Open AD Kit system is referred to as a **Deployment**. A deployment is a specific combination of **Autoware components and tools**, configured to work together to achieve a particular task, such as a planning simulation or a full autonomous driving stack for a specific vehicle.

## Sample Deployments

Sample deployment configurations to help you get started. Recommended for **learning and development**.

- [Sample Deployments](https://github.com/autowarefoundation/openadkit/tree/main/deployments/samples)

## Demo Deployments

[Demo deployment](https://github.com/autowarefoundation/openadkit/tree/main/deployments/demos) configurations that are specific to certain **use case scenarios**.

- [Zenoh-bridge](zenoh-bridge/index.md)

    The `zenoh-bridge` provides the communication backbone for the OpenADKit's distributed architecture. It demonstrates a "Cloud-Edge" deployment model by seamlessly bridging two isolated ROS 2 environments, decoupling compute-intensive components from lightweight visualization tools.

    In this model, the core `autoware` stack runs on an **edge device** (e.g., a vehicle or server), while the `visualizer` can be accessed remotely from a user's machine (the **cloud side**).
