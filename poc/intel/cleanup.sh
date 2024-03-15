#!/bin/bash
set -e

echo -e "Cleaning up MicroK8s"
sudo snap remove microk8s --purge
sudo snap remove kubectl
