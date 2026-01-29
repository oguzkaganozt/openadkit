# Open AD Kit Components

[Open AD Kit](https://autoware.org/open-ad-kit/) offers containers for Autoware Components to simplify the deployment of Autoware and its dependencies. This directory contains scripts to build Component containers.

Detailed instructions on how to deploy the components can be found in the [Open AD Kit Deployments](https://autowarefoundation.github.io/openadkit/deployments/).

## Build Pipeline

```mermaid
flowchart TB
    subgraph base["Base Images"]
        B[autoware-base]
        BC[autoware-base-cuda]
    end

    subgraph intermediate["Intermediate Images"]
        RD[rosdep-depend]
        CD[core-devel]
        ACD[autoware-common-devel]
        ACDC[autoware-common-devel-cuda]
    end

    subgraph runtime["Runtime Images"]
        SP[sensing-perception]
        LM[localization-mapping]
        PC[planning-control]
        VS[vehicle-system]
        VIZ[visualization]
        API[api]
    end

    subgraph runtime_cuda["Runtime Images (CUDA)"]
        SPC[sensing-perception-cuda]
        UNIC[autoware-cuda]
    end

    %% Base flow
    B --> BC
    B --> RD
    B --> CD
    CD --> ACD
    BC --> ACDC

    %% Runtime dependencies
    ACD --> SP
    ACD --> LM
    ACD --> PC
    ACD --> VS
    ACD --> VIZ
    ACD --> API

    %% CUDA runtime
    ACDC --> SPC
    ACDC --> UNIC

    %% rosdep provides deps to all
    RD -.->|deps| SP
    RD -.->|deps| LM
    RD -.->|deps| PC
    RD -.->|deps| VS
    RD -.->|deps| API
    RD -.->|deps| SPC
    RD -.->|deps| UNIC
```

### Build Groups

| Group | Description | Targets |
|-------|-------------|---------|
| `default` | All images | intermediate + runtime |
| `intermediate` | Build dependencies | rosdep-depend, core-devel, autoware-common-devel |
| `runtime` | Final component images | sensing-perception, localization-mapping, planning-control, vehicle-system, visualization, api |
