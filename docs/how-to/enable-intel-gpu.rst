.. _enable_intel_gpu:

Enable Intel GPUs
=============================

This guide describes how to configure DSS to utilise the Intel GPUs on your machine. This can be done by enabling the Intel device plugin on your MicroK8s cluster.

Prerequisites
-------------

* :ref:`DSS is installed <install_DSS_CLI>` and :ref:`initialised <initialise_DSS>`.
* Your machine has an Intel GPU.

Install the Intel GPU plugin
----------------------------

To ensure DSS can utilise Intel GPUs:
1. The Intel GPU drivers must be installed.
2. MicroK8s must be set up to utilise the Intel GPU drivers.   

Verify the Intel GPU drivers are installed in your machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To confirm that your machine has the Intel GPU drivers set up, install the `intel-gpu-tools` package:

.. code-block:: bash

   sudo apt install intel-gpu-tools

And list the Intel GPU devices on your machine as follows:

.. code-block:: bash

   intel_gpu_top -L

If the drivers are correctly installed, you should receive information about your GPU device from the command's output.

.. note::
   For Intel discrete GPUs on older versions of Ubuntu like 22.04, you may need to perform additional steps like install a `HWE kernel <https://ubuntu.com/kernel/lifecycle>`_.   

Install the kubectl snap
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, install the `kubectl` snap package:

.. code-block:: bash
				
  sudo snap install kubectl --classic

Create a configuration file so that `kubectl` can communicate with MicroK8s by running:

.. code-block:: bash
				
  mkdir -p ~/.kube
  microk8s config > ~/.kube/config

Enable the Intel GPU plugin in your Kubernetes cluster 
------------------------------------------------------

To ensure DSS can utilise Intel GPUs, you have to enable the Intel GPU plugin in your Kubernetes cluster. To enable the plugin, you must download the appropriate `kustomization.yaml` files from `Intel device plugins for Kubernetes`_ repository, run `kubectl kustomize` to build YAML configuration files, and then apply them on your MicroK8s cluster.

Now, build the YAML files for Node Feature Discovery, Node Feature Rules, and the GPU plugin by running the following:

.. code-block:: bash

  VERSION=v0.30.0
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=${VERSION} > node_feature_discovery.yaml
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=${VERSION} > node_feature_rules.yaml
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=${VERSION} > gpu_plugin.yaml

To allow multiple containers to utilise the same GPU, run:

.. code-block:: bash
				
  sed -i 's/enable-monitoring/enable-monitoring\n        - -shared-dev-num=10/' gpu_plugin.yaml

Then, apply the built YAML files to your MicroK8s cluster by running:

.. code-block:: bash
				
  kubectl apply -f node_feature_discovery.yaml
  kubectl apply -f node_feature_rules.yaml
  kubectl apply -f gpu_plugin.yaml

The MicroK8s cluster is now configured to recognise and utilise your Intel GPU.

.. note::
 After the YAML configuration files have been applied, they can be safely deleted.

Verify the Intel GPU plugin is installed
----------------------------------
To verify the Intel GPU plugin is installed and the MicroK8s cluster recognises your GPU, run:

.. code-block:: bash

   kubectl get nodes --show-labels | grep intel

You should receive non-empty output with the name of your cluster.   
 
Verify DSS detects the GPU
----------------------------------

Verify DSS has detected the GPU by checking the DSS status. To do so, run the following command using the DSS CLI: 

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

* To enable the NVIDIA GPUs on your machine, see :ref:`nvidia_gpu`.
* To learn how to manage your DSS environment, check :ref:`manage_DSS`.
* If you are interested in managing Jupyter Notebooks within your DSS environment, see :ref:`manage_notebooks`.
