.. _enable_intel_gpu:

Enable Intel GPUs
=================

This guide describes how to configure Data Science Stack (DSS) to utilise the Intel GPUs on your machine. 

You can do so done by enabling the Intel device plugin on your `MicroK8s`_ cluster.

Prerequisites
-------------

* Ubuntu 24.04.
* DSS is :ref:`installed <install_DSS_CLI>` and :ref:`initialised <initialise_DSS>`.
* The `kubectl snap <https://snapcraft.io/kubectl>`_ package is installed.
* Your machine includes an Intel GPU.

.. note::
   After installing `kubectl`, configure MicroK8s to run `kubectl` commands as follows:

   .. code-block:: bash

      mkdir -p ~/.kube
      microk8s config > ~/.kube/config 

Verify the Intel GPU drivers
----------------------------------------------------------

To confirm that your machine has the Intel GPU drivers set up, first install the `intel-gpu-tools` package:

.. code-block:: bash

   sudo apt install intel-gpu-tools

Now list the Intel GPU devices on your machine as follows:

.. code-block:: bash

   intel_gpu_top -L

If the drivers are correctly installed, you should see information about your GPU device such as the following:

.. code-block::

   card0                    8086:56a0
   pci:vendor=8086,device=56A0,card=0
   └─renderD128 

.. note::
   For Intel discrete GPUs on Ubuntu versions older than 24.04, you may need to perform additional steps such as installing a `HWE kernel <https://ubuntu.com/kernel/lifecycle>`_. 

Enable the Intel GPU plugin 
------------------------------------------------------

To ensure DSS can utilise Intel GPUs, you have to enable the Intel GPU plugin in your MicroK8s cluster.

1. Use `kubectl kustomize` to build the plugin YAML configuration files:

.. code-block:: bash

  VERSION=v0.30.0
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=${VERSION} > node_feature_discovery.yaml
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=${VERSION} > node_feature_rules.yaml
  kubectl kustomize https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=${VERSION} > gpu_plugin.yaml

To allow multiple containers to utilise the same GPU, run:

.. code-block:: bash
                
  sed -i 's/enable-monitoring/enable-monitoring\n        - -shared-dev-num=10/' gpu_plugin.yaml

2. Apply the built YAML files to your MicroK8s cluster:

.. code-block:: bash
                
  kubectl apply -f node_feature_discovery.yaml
  kubectl apply -f node_feature_rules.yaml
  kubectl apply -f gpu_plugin.yaml

The MicroK8s cluster is now configured to recognise and utilise your Intel GPU.

.. note::
 After the YAML configuration files have been applied, they can be safely deleted.

Verify the Intel GPU plugin
-------------------------------------------------
To verify the Intel GPU plugin is installed and the MicroK8s cluster recognises your GPU, run:

.. code-block:: bash

   kubectl get nodes --show-labels | grep intel

You should see an output with the cluster name such as the following:

.. code-block:: bash

   kubectl get nodes --show-labels | grep intel
   fluent-greenshank   Ready    <none>   18s   v1.30.3   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,intel.feature.node.kubernetes.io/gpu=true

Verify DSS detects the GPU
----------------------------------

Verify DSS has detected the GPU by checking the DSS status. To do so, run the following command using the DSS CLI: 

.. code-block:: bash

  dss status

You should expect an output like this:

.. code-block:: bash
                
  Output:
  MLflow deployment: Ready
  MLflow URL: http://10.152.183.68:5000
  NVIDIA GPU acceleration: Disabled
  Intel GPU acceleration: Enabled

See also
--------

* To learn how to manage your DSS environment, check :ref:`manage_DSS`.
* If you are interested in managing Jupyter Notebooks within your DSS environment, see :ref:`manage_notebooks`.
