#!/bin/bash

# This needs to be a separate file as newgrp will not have effect from setup_environment.sh
echo "Using addons: $MICROK8S_ADDONS"
microk8s enable storage $MICROK8S_ADDONS
microk8s kubectl rollout status deployment/hostpath-provisioner -n kube-system

# Wait for gpu operator components to be ready
while ! kubectl logs -n gpu-operator -l app=nvidia-operator-validator | grep "all validations are successful"
do
  echo "waiting for validations"
  sleep 5
done

# Setup config
microk8s config > ~/.kube/config
chown ubuntu:ubuntu ~/.kube/config
chmod 600 ~/.kube/config
