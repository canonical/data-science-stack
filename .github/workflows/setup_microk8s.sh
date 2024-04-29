#!/bin/bash

# This needs to be a separate file as newgrp will not have effect from  setup_environment.sh
sudo microk8s enable storage dns rbac gpu
microk8s kubectl rollout status deployment/hostpath-provisioner -n kube-system

# Install + setup kubectl
sudo snap install kubectl --classic
microk8s config > /home/ubuntu/.kube/config
