#!/bin/bash

# Ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

# Python setup
export DEBIAN_FRONTEND=noninteractive
apt-get update -yqq
apt-get install -yqq python3-pip
pip3 install tox

# Restart the systemd service
systemctl restart snapd.service

# Canonical k8s setup
sudo snap install kubectl --classic
sudo snap install k8s --classic --channel=1.32-classic/stable
sudo k8s bootstrap
sudo k8s enable local-storage
mkdir -p ~/.kube
sudo k8s config > ~/.kube/config