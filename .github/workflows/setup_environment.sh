#!/bin/bash

# Ensure the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

# Python setup
apt-get update -yqq
apt-get install -yqq python3-pip
pip3 install tox

# Microk8s setup
snap install microk8s --channel=1.28/stable --classic
usermod -a -G microk8s ubuntu
newgrp microk8s
