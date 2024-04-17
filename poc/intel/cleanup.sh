#!/bin/bash
set -e

echo -e "Draining microk8s nodes"
for node in $(sudo microk8s kubectl get nodes -o name); do
  sudo microk8s kubectl drain --ignore-daemonsets --delete-emptydir-data "${node}"
done
echo -e "Cleaning up MicroK8s"
sudo snap remove microk8s --purge
sudo snap remove kubectl
echo -e "Removed microK8s and DSS successfully!"
