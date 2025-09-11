# Open AD Kit: Logging Simulation

This sample deployment shows how to run the logging simulation deployment sample.

- **autoware**: Autoware monolithic container for development and deployment.
- **scenario-simulator**: Simulation container for Autoware scenario testing.
- **visualizer**: RViz-based remote operation and visualization container for Autoware.

## Requirements

In order to run the logging simulation sample deployment, you need to have the logging **sample map** and **rosbag**. You can download them by running the following command:

### Autoware Sample Logging Map

Download and unpack a sample map that is used in this sample.

- You can also download [the map](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view?usp=sharing) manually.

```bash
gdown -O ~/autoware_map/ 'https://docs.google.com/uc?export=download&id=1499_nsbUbIeturZaDj7jhUownh5fvXHd'
unzip -d ~/autoware_map ~/autoware_map/sample-map-logging.zip
```

> **Note**: This sample map(Copyright 2020 TIER IV, Inc.) is only for demonstration purposes. You can use your own map by following the [How-to Guide](https://autowarefoundation.github.io/autoware-documentation/main/how-to-guides/integrating-autoware/creating-maps/).

### Autoware Sample Rosbag

Download and unpack a sample rosbag that is used for **sensor simulation** in this sample.

- You can also download [the rosbag](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view?usp=sharing) manually.

```bash
gdown -O ~/autoware_map/ 'https://docs.google.com/uc?export=download&id=1sU5wbxlXAfHIksuHjP3PyI2UVED8lZkP'
unzip -d ~/autoware_map/ ~/autoware_map/sample-rosbag.zip
```

> **Note**: Due to privacy concerns, the rosbag(Copyright 2020 TIER IV, Inc.) does not contain image data, which will cause: Traffic light recognition functionality cannot be tested with this sample rosbag. Object detection accuracy is decreased.

## To Run

```bash
docker-compose -f docker-compose.yaml up -d
```
