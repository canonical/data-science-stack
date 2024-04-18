#!/bin/bash
set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SUPPORTED_APPS="itex ipex openvino"
OPENVINO_IMAGE="local/openvinotoolkit:render-addon"
OPENVINO_TAR_IMAGE="openvino.tar"
TIMEOUT=1200s

usage() {
  cat <<EOM
Usage: ./$(basename "${BASH_SOURCE[0]}") <app>

Deploy application in Jupyter Notebook with Intel GPU support.

Supported applications: ${SUPPORTED_APPS}
EOM
}

app=$1
if echo "${SUPPORTED_APPS}" | tr " " "\n" | grep -Fqx "${app}" ; then
  if [ "${app}" = "openvino" ]; then
    IMAGE_AGE=$(docker image ls --format '{{.CreatedSince}}' ${OPENVINO_IMAGE})
    if [ -z "${IMAGE_AGE}" ]; then
      echo "Docker image ${OPENVINO_IMAGE} not found." \
           "Please build it using the provided shell script and re-run this script."
      exit 1
    fi
    echo -e "\nFound ${OPENVINO_IMAGE} Docker image, built ${IMAGE_AGE}"
    sleep 3
  fi
  echo -e "\nSetting up DSS for application ${app} with Intel GPU support"
else
  echo "Unsupported app: ${app}"
  usage
  exit 1
fi

echo -e "\nStep 1/3: Deploying MicroK8s snap"
sudo snap install microk8s --classic --channel=1.29/stable

sudo usermod -a -G microk8s $USER
sudo mkdir -p $HOME/.kube
sudo mkdir -p $HOME/.local/share
sudo chown -f -R $USER $HOME/.kube
sudo chown -f -R $USER $HOME/.local/share

echo -e "\nStep 2/3: Configuring MicroK8s addons"
sudo microk8s enable dns
sudo microk8s enable hostpath-storage
sudo microk8s enable rbac

echo "Waiting for microK8s addons to become ready..."
sudo microk8s.kubectl wait \
  --for=condition=available \
  --timeout $TIMEOUT \
  -n kube-system \
  deployment/coredns \
  deployment/hostpath-provisioner
sudo microk8s.kubectl -n kube-system rollout status ds/calico-node

echo -e "\nStep 3/3: Configuring Intel runtime"
if microk8s kubectl get pods -o name | grep -q "intel-gpu-plugin"; then
  echo "WARNING: active Intel GPU-enabled pod detected." \
       "You may need to run the cleanup script before deploying another application."
  sleep 5
fi

# https://github.com/canonical/microk8s/issues/4453
sudo snap install kubectl --classic
sudo microk8s kubectl config view --raw > $HOME/.kube/config

# install device plugin
kubectl apply -k 'https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=v0.29.0'
kubectl apply -k 'https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=v0.29.0'
kubectl apply -k 'https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=v0.29.0'
sleep 5

# wait
kubectl -n node-feature-discovery rollout status ds/nfd-worker
kubectl -n default rollout status ds/intel-gpu-plugin

echo -e "\n\$ dss initialise"
sudo microk8s kubectl apply -f $SCRIPT_DIR/../common-manifests/namespace.yaml
sudo microk8s kubectl apply -f $SCRIPT_DIR/../common-manifests/mlflow.yaml
sudo microk8s kubectl apply -f $SCRIPT_DIR/../common-manifests/notebooks.yaml

sudo microk8s.kubectl wait \
  --for condition=available \
  --timeout $TIMEOUT \
  -n dss\
  deployment \
  -l app=dss-mlflow

launch_notebook() {
  local fullname=$1
  echo -e "\n\$ dss start ${app} notebook"
  sudo microk8s kubectl apply -f $SCRIPT_DIR/manifests/notebook-${app}.yaml
  sudo microk8s.kubectl wait \
    --for condition=available \
    --timeout $TIMEOUT \
    -n dss\
    deployment \
    -l app=user-notebook-${fullname}

  echo -e "\n\$ dss status"
  MLFLOW_IP=$(sudo microk8s.kubectl get svc \
    -n dss \
    -o jsonpath="{.spec.clusterIP}" \
    mlflow)
  NOTEBOOK_IP=$(sudo microk8s.kubectl get svc \
    -n dss \
    -o jsonpath="{.spec.clusterIP}" \
    user-notebook-${fullname})

  echo "DSS has started successfully!

  For next steps you can connect to either of the following IPs and
  start experimenting:

  mlflow: http://$MLFLOW_IP
  ${fullname} notebook: http://$NOTEBOOK_IP
  """
}

if [ "${app}" = "openvino" ]; then
  echo -e "\n\$ Importing OpenVINO Docker image into microk8s"
  docker save local/openvinotoolkit:render-addon > ${OPENVINO_TAR_IMAGE}
  microk8s ctr image import ${OPENVINO_TAR_IMAGE}
  rm -f ${OPENVINO_TAR_IMAGE}
  launch_notebook "openvino"
  # example:
  # https://github.com/openvinotoolkit/openvino_notebooks/blob/main/notebooks/108-gpu-device/108-gpu-device.ipynb
elif [ "${app}" = "ipex" ]; then
  launch_notebook "pytorch"
  # example:
  # https://intel.github.io/intel-extension-for-pytorch/xpu/latest/tutorials/examples.html#float32
elif [ "${app}" = "itex" ]; then
  launch_notebook "tensorflow"
  # example:
  # https://github.com/intel/intel-extension-for-tensorflow/blob/main/examples/quick_example.md
fi

