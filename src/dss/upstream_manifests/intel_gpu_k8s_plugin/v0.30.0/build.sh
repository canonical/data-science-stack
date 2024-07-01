#!/bin/bash
#
# Build the K8s manifests locally for the Intel GPU plugin
# and its dependencies. This is done partly as a workaround
# for a microk8s bug that prevents manifests from being
# applied from a GitHub URL. The workaround is to use
# kubectl directly (instead of the one distributed via the
# microk8s snap) to pull down the manifests from GitHub.
#
# Note, this script only needs to be run once to generate
# the manifests for a particular version on a system
# where the kubectl snap is installed. The script is kept here
# for reference and reproducibility to support future releases
# of the GPU plugin.
#

VERSION=v0.30.0

kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=${VERSION} > node_feature_discovery.yaml
kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=${VERSION} > node_feature_rules.yaml
kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=${VERSION} > gpu_plugin.yaml
# Allow (at most) ten containers to share GPU, see:
# https://github.com/intel/intel-device-plugins-for-kubernetes/issues/1769
sed -i 's/enable-monitoring/enable-monitoring\n        - -shared-dev-num=10/' gpu_plugin.yaml
