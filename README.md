<div align="center">

# Data Science Stack ✨

*Making it seamless to run GPU enabled containerized ML Environments*

</div>

## Overview

The Data Science Stack (DSS) makes it seamless for everyone to jump into an ML Environment within minutes and be able to utilise their GPUs.

DSS is a ready-made environment which allows everyone to run ML workloads on the laptop.
It gives easy access to a solution for developing and optimising ML models, that leverages the GPUs of the laptop by
enabling users to utilise different ML environment images based on their needs.

The DSS is a stack that includes
- a container orchestration system ([microK8s](https://microk8s.io/) snap)
- out-of-the box containerized ML Environments
- an intuitive CLI which streamlines the management of those containers (data-science-stack snap)

The container orchestration system also handles the integration with the host's
GPU and drivers, so the containerized environments can only focus on user-space libraries.

## Features

- Containerized environment management
- Seamless GPU utilization
- Out-of-the box ML Environments with JupyterLab
- Easy data passing between local machine and containerized ML Environments
- [MLFlow](https://github.com/mlflow/mlflow) for lineage tracking

## Requirements

- Ubuntu 22.04
- [Snapcraft](https://snapcraft.io/) (included in Ubuntu)

## Quick Start

🚧🚧

## Development

To get started with developing the DSS locally you'll need to:
1. Have microK8s snap installed
2. Build the `dss` snap locally and execute its commands

The above can be achieved with the following commands
```bash
sudo snap install microk8s --channel=1.28/stable --classic
microk8s enable storage dns rbac
microk8s config > ./kubeconfig

sudo snap install snapcraft --classic
snapcraft
snap install data-science-stack-<name>.snap --dangerous
snap connect data-science-stack:dot-dss-config

dss --help
```

If you also have an NVIDIA GPU you can enable it with the following command:
```bash
microk8s enable gpu
```

🚧🚧

## Resources

🚧🚧

## Feedback

🚧🚧
