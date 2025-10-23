# Workloads

Open AD Kit is a workload based project, which means that it is designed to be deployed on a variety of platforms with microservices architecture. Each workload is designed to be independent and can be deployed on a variety of platforms.

![Granular Workloads](../assets/images/granular-workloads.png)

## Autoware Workloads

### Sensing

The sensing workload is responsible for collecting data from the vehicle's sensors. Sensing workload can be configured to collect data from a variety of sensors, including **cameras, lidars, and radars**. For more details on the [Autoware sensing design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/sensing/).

### Perception

The perception workload is responsible for processing the data from the vehicle's sensors and creating a map of the environment. Perception workload can be configured to use a variety of perception algorithms, including **object detection, tracking, and mapping**. For more details on the [Autoware perception design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/perception/).

### Mapping

The mapping workload is responsible for creating a map of the environment. Mapping workload can be configured to use a variety of mapping algorithms, including **occupancy grid mapping and point cloud mapping**. For more details on the [Autoware mapping design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/mapping/).

### Localization

The localization workload is responsible for determining the vehicle's position in the map. Localization workload can be configured to use a variety of localization algorithms, including **GPS, IMU, and visual odometry**. For more details on the [Autoware localization design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/localization/).

### Planning

The planning workload is responsible for planning the vehicle's path. Planning workload can be configured to use a variety of planning algorithms, including **Route Planning, Goal Planning, and Behavior Planning**. For more details on the [Autoware planning design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/planning/).

### Control

The control workload is responsible for controlling the vehicle's actuators. Control workload can be configured to use a variety of control algorithms, including **PID and MPC**. For more details on the [Autoware control design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/control/).

### Vehicle

The vehicle workload is responsible for managing the vehicle's state. Vehicle workload can be configured to use a variety of vehicle algorithms, including **vehicle state estimation and vehicle control**. For more details on the [Autoware vehicle design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/vehicle/).

### System

The system workload is responsible for managing the vehicle's system. System workload can be configured to use a variety of system algorithms, including **system health monitoring and system error handling**. For more details on the [Autoware system design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture/system/).

### API

The API workload is responsible for providing [AD API](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-interfaces/ad-api/) interface for the vehicle's state. API workload can be configured to enable/disable various interfaces. For more details on the [Autoware interfaces design document](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-interfaces/).
