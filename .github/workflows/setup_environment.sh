#!/bin/bash

# Python setup
sudo apt-get update -yqq
sudo apt-get install -yqq python3-pip
sudo --preserve-env=http_proxy,https_proxy,no_proxy pip3 install tox
python --version

# Microk8s setup
sudo snap install microk8s --channel=1.28/stable --classic
sudo usermod -a -G microk8s ubuntu
mkdir -p /home/ubuntu/.kube
sudo chown -f -R ubuntu /home/ubuntu/.kube
newgrp microk8s