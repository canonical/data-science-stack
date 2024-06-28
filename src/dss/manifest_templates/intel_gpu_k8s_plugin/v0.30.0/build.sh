#!/bin/bash
#
# Build an "uber" manifest locally of the Intel
# K8s GPU Plugin. This is done partly as a workaround
# for a microk8s bug that prevents manifests from being
# applied from a GitHub URL. The workaround is to use
# kubectl directly (instead of the one distributed via the
# microk8s snap) to pull down the manifests from GitHub,
# then we combine the three parts into one "uber" manifest
# for convenience and to ensure correct resource ordering.
#
# Note, this script only needs to be run once to generate
# the "uber" manifest for a particular version on a system
# where the kubectl snap is installed. It is only kept here
# for reference and reproducibility to support future releases
# of the GPU plugin.
#

VERSION=v0.30.0
UBER_YAML=combined.yaml

kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=${VERSION} > ${UBER_YAML}
echo "---" >> ${UBER_YAML}
kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=${VERSION} >> ${UBER_YAML}
echo "---" >> ${UBER_YAML}
kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=${VERSION} >> ${UBER_YAML}
