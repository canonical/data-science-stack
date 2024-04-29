#!/bin/bash

# Microk8s setup
sudo snap install microk8s --channel=1.28/stable --classic
sudo usermod -a -G microk8s ubuntu
mkdir -p /home/ubuntu/.kube
sudo chown -f -R ubuntu /home/ubuntu/.kube
newgrp microk8s