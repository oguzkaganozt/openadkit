# Planning Simulation

Run the Autoware planning and control stack on a sample map with the built-in
simulator, then set a route in RViz in your browser. No GPU is required; with
an NVIDIA GPU, `--gpu` plans with Autoware 2.0's Diffusion Planner.

Complete the [Quickstart](../../getting-started/index.md) setup first. For GPU
mode, run `openadkit setup --gpu --verify`.

## Run

```bash
openadkit run planning-simulation         # CPU: the rule-based planner
openadkit run planning-simulation --gpu   # GPU: the Diffusion Planner (amd64 only)
```

--8<-- "includes/ros-distro.md"

`run` downloads the sample map, pulls the images and starts the stack. The
sample map is Copyright 2020 TIER IV, Inc. and is provided for demonstration
only.

### GPU Mode {: #gpu-mode }

!!! warning "Experimental"
    The GPU mode may change in a minor release. See
    [Compatibility](../../releases/compatibility.md#experimental).

With `--gpu`, the planning service runs the `planning-cuda` image with
`planning_setting:=diffusion_planner`, and `run` also downloads the Diffusion
Planner v5.0 model from Hugging Face to
`~/autoware_data/ml_models/diffusion_planner/v5.0`. The first start builds a
TensorRT engine from the model there, so it takes longer than later starts.

Control and the rest of the stack are the same in both modes: control follows
`/planning/trajectory`, whichever planner makes it. See
[Autoware Architecture 2.0](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-architecture-v2/)
for the planner. CI evidence runs the CPU mode; the GPU mode is checked by
hand on a GPU host.

!!! warning "Known limitation"
    Autoware 2.0.0's Diffusion Planner can stop the
    ego up to about 2 m before the goal, so the route does not become `ARRIVED`
    and `run --gpu --verify` fails on the sample route. This is the planner's own
    output, reproduced with upstream's image
    ([autoware_universe#13603](https://github.com/autowarefoundation/autoware_universe/issues/13603)).

## Open the Visualizer

--8<-- "includes/visualizer-remote-access.md"

In RViz, set an initial pose and a goal pose, then watch the vehicle drive the
route. See the
[Autoware planning simulation guide](https://autowarefoundation.github.io/autoware-documentation/main/demos/planning-sim/lane-driving/#2-set-an-initial-pose-for-the-ego-vehicle)
for details.

## Stop and Recover

```bash
openadkit stop
```

To replace missing or incomplete map data, run
`openadkit fetch planning-simulation --force`. For other issues, see
[Troubleshooting](../../getting-started/troubleshooting.md).
