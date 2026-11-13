# Reference Designs

An [Autoware Reference Design](https://docs.autoware.org/main/reference-design/)
combines a Deployment Profile (the vehicle, the operating conditions and the
use case) with a Reference Software Stack (the modules, the model versions and
the parameters), so that others can reproduce the system. A kit is the form in
which Open AD Kit holds such a software stack: it pins every part, and one
command runs it.

No Reference Design is published as a kit. This page shows how the two
fit.

## What Goes Where

| Part of a Reference Design | In a kit |
| --- | --- |
| Autoware version | `extends`: one Open AD Kit release, which pins one Autoware release and its images |
| Modules | The base deployment's services, your packages in `overlay_ws/` and your extra services |
| Model versions | `data` in `deployment.json`: each download with its URL and SHA-256 |
| Parameters | `config/autoware/` and `settings.env` |
| Vehicle and sensors | `VEHICLE_MODEL` and `SENSOR_MODEL`, with the vehicle's description and launch packages in `overlay_ws/` ([A New Vehicle](kit-guide.md#a-new-vehicle)) |
| Evaluation and testing | The `verify` step, which `openadkit run --verify` runs |

The Deployment Profile stays in the Reference Design's own documents: the
hardware, the operational design domain and the use case. The kit states only
what it needs from the host, in `requirements`: architectures, ROS distros and
GPU.

## Publish One as a Kit

1. Start a kit on the simulation deployment that fits the design, for example
   `openadkit new my-design --base scenario-simulation`
   ([Create a Kit](create-a-kit.md)).
2. Add the stack through the kit's
   [extension points](kit-guide.md#extension-points): packages,
   parameters, models and extra services.
3. Name a `verify` step of your own in `deployment.json` that checks what the
   Reference Design states, such as the rates of planning and control
   ([Validation and Evidence](kit-guide.md#validation-and-evidence)).
4. Commit the kit directory to the Reference Design's repository. A reader
   reproduces the stack there with `openadkit build` and
   `openadkit run --verify`; the CLI downloads the release the kit pins on
   first use.

## Limits

- **Simulation only.** Every catalog deployment is a simulation, so a kit shows
  the stack in simulation, not on the vehicle.
- **A base is required.** A kit deployment builds on a base deployment. A stack
  that does not run the Autoware Universe pipeline, such as
  [Vision Pilot](https://github.com/autowarefoundation/vision_pilot), cannot be
  a kit.
