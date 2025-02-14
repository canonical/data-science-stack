#!/bin/bash

# Setup python 3.10 with tox
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y
sudo apt install python3.10 python3.10-distutils python3.10-venv -y
wget https://bootstrap.pypa.io/get-pip.py
python3.10 get-pip.py
python3.10 -m pip install tox
rm get-pip.py

# Removing docker as it is blocking canonical k8s bootstrap
sudo apt-get remove -y docker-ce docker-ce-cli containerd.io
sudo rm -rf /run/containerd

# Setup Canonical k8s
sudo snap install kubectl --classic
sudo snap install k8s --classic --channel=1.32-classic/stable
sudo k8s bootstrap
sudo k8s enable local-storage
mkdir -p ~/.kube
sudo k8s config > ~/.kube/config

# Setup Nvidia k8s operator
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh
helm install --wait --generate-name -n gpu-operator --create-namespace nvidia/gpu-operator
while ! kubectl logs -n gpu-operator -l app=nvidia-operator-validator | grep "all validations are successful"
do   
    echo "waiting for validations"
    sleep 5
done
