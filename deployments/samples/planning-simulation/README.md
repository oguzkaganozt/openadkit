# Autoware Planning Simulation

This sample deployment shows how to run the planning simulation deployment sample.

- **autoware**: Autoware monolithic container for development and deployment.
- **scenario-simulator**: Simulation container for Autoware scenario testing.
- **visualizer**: RViz-based remote operation and visualization container for Autoware.

## Requirements

In order to run the planning simulation sample deployment, you need to have the planning **sample map**. You can download it by running the following command:

### Sample Planning Map

Download and unpack a sample map that is used in this sample.

- You can also download [the map](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view?usp=sharing) manually.

```bash
gdown -O ~/autoware_map/ 'https://docs.google.com/uc?export=download&id=1499_nsbUbIeturZaDj7jhUownh5fvXHd'
unzip -d ~/autoware_map ~/autoware_map/sample-map-planning.zip
```

> **Note**: This sample map(Copyright 2020 TIER IV, Inc.) is only for demonstration purposes. You can use your own map by following the [How-to Guide](https://autowarefoundation.github.io/autoware-documentation/main/how-to-guides/integrating-autoware/creating-maps/).

## To Run

```bash
docker-compose -f docker-compose.yaml up -d
```
