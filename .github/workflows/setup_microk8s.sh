#!/bin/bash

# This needs to be a separate file as newgrp will not have effect from setup_environment.sh
microk8s enable storage dns rbac gpu
microk8s kubectl rollout status deployment/hostpath-provisioner -n kube-system

# Wait for gpu operator components to be ready
while ! sudo microk8s.kubectl logs -n gpu-operator-resources -l app=nvidia-operator-validator | grep "all validations are successful"
do
  echo "waiting for validations"
  sleep 5
done

# Setup config
microk8s config > ~/.kube/config
chown ubuntu:ubuntu ~/.kube/config
chmod 600 ~/.kube/config