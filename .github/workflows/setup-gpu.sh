#!/bin/bash

# Ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

# Setup Nvidia k8s operator
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh

helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
    && helm repo update

# Ensure KUBECONFIG is set
export KUBECONFIG=~/.kube/config

# Install GPU operator
helm install --wait --generate-name -n gpu-operator --create-namespace nvidia/gpu-operator

# Wait until the GPU operator validations pass
while ! kubectl logs -n gpu-operator -l app=nvidia-operator-validator | grep "all validations are successful"; do
    echo "Waiting for GPU operator validations to pass..."
    sleep 5
done

