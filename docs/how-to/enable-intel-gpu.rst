.. _enable_intel_gpu:

Enable Intel GPUs
=============================

This guide describes how to configure DSS to utilise the Intel GPUs on your machine. This can be done by enabling the Intel device plugin on your MicroK8s cluster.

Prerequisites
-------------

* :ref:`MicroK8s is installed <set_microk8s>`.
* :ref:`DSS CLI is installed <install_DSS_CLI>`.
* The Intel GPU is recognised by your machine. This can be confirmed by running `intel_gpu_top` from the `intel-gpu-tools` package. For discrete GPUs on older versions of Ubuntu like 22.04, you may need to perform additional steps like install a HWE kernel.

Install the kubectl snap
---------------------------
First, install the `kubectl` snap package:

.. code-block:: bash
				
  sudo snap install kubectl -–classic

Create a configuration file so that `kubectl` can communicate with MicroK8s by running:

.. code-block:: bash
				
  mkdir -p ~/.kube
  microk8s config > ~/.kube/config

Enable the Intel GPU plugin in your Kubernetes cluster 
------------------------------------------------------

To ensure DSS can utilise Intel GPUs, you have to enable the Intel GPU plugin in your Kubernetes cluster. The plugin uses `Node Feature Discovery <https://github.com/kubernetes-sigs/node-feature-discovery>`_ to detect whether an Intel GPU exists on a machine. You can see `this page <https://github.com/kubernetes-sigs/node-feature-discovery>`_ for more details.

To enable the plugin, you must download the appropriate `kustomization.yaml` files from Intel’s `device plugins for Kubernetes <https://github.com/intel/intel-device-plugins-for-kubernetes>`_ repository, and then apply them on your MicroK8s cluster.

First, build the YAML files for Node Feature Discovery, Node Feature Rules, and the GPU plugin, by running:

.. code-block:: bash

  VERSION=v0.30.0
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=${VERSION} > node_feature_discovery.yaml
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=${VERSION} > node_feature_rules.yaml
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=${VERSION} > gpu_plugin.yaml

To allow multiple containers to utilise the same GPU, run:

.. code-block:: bash
				
  sed -i 's/enable-monitoring/enable-monitoring\n        - -shared-dev-num=10/' gpu_plugin.yaml

Then, apply the created YAML files to your MicroK8s cluster by running:

.. code-block:: bash
				
  kubectl apply -f node_feature_discovery.yaml
  kubectl apply -f node_feature_rules.yaml
  kubectl apply -f gpu_plugin.yaml

The MicroK8s cluster should now be configured to recognise and utilise your Intel GPU.

.. note::
 After the YAML configuration files have been applied, they can be safely deleted.

Finally, 

Verify the DSS CLI detects the GPU
----------------------------------

Initialise the DSS CLI by running:

.. code-block:: bash
				
  dss initialize --kubeconfig=$(microk8s config)

Verify the DSS CLI has detected the GPU by checking the DSS status as follows:

.. code-block:: bash

  dss status

You should expect an output like this:

.. code-block:: bash
				
  Output:
  [INFO] MLflow deployment: Ready
  [INFO] MLflow URL: http://10.152.183.68:5000
  [INFO] NVIDIA GPU acceleration: Disabled
  [INFO] Intel GPU acceleration: Enabled

See also
--------

* To enable
* To learn how to manage your DSS environment, check :ref:`manage_DSS`.
* If you are interested in managing Jupyter Notebooks within your DSS environment, see :ref:`manage_notebooks`.
