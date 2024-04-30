#!/bin/bash

# This needs to be a separate file as newgrp will not have effect from setup_environment.sh
microk8s enable storage dns rbac gpu
microk8s kubectl rollout status deployment/hostpath-provisioner -n kube-system

# Install + setup kubectl
snap install kubectl --classic
microk8s config > ~/.kube/config
chown ubuntu:ubuntu ~/.kube/config
chmod 600 ~/.kube/config