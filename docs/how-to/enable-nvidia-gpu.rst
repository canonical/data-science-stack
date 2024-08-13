.. _nvidia_gpu:

Enable NVIDIA GPUs
==================

This guide describes how to configure DSS to utilise your NVIDIA GPUs.

You can do so by configuring the underlying MicroK8s, on which DSS relies on for running the containerised workloads.

Prerequisites
-------------

* :ref:`DSS CLI is installed <install_DSS_CLI>` and :ref:`initialised <initialise_DSS>`.
* Your machine has an NVIDIA GPU.  

.. _install_nvidia_operator:

Install the NVIDIA Operator
---------------------------

To ensure DSS can utilise NVIDIA GPUs:

1. The NVIDIA drivers must be installed.
2. MicroK8s must be set up to utilise NVIDIA drivers.

MicroK8s is leveraging the `NVIDIA Operator`_ for setting up and configuring the NVIDIA runtime. 
The NVIDIA Operator also installs the NVIDIA drivers, if they are not present already on your machine.

To enable the NVIDIA runtimes on MicroK8s, run the following command:

.. code-block:: bash

   sudo microk8s enable gpu

.. note::
   The NVIDIA Operator detects the installed NVIDIA drivers in your machine. 
   If they are not installed, it will do so automatically.

Verify the NVIDIA Operator is up
--------------------------------

Before spinning up workloads, the GPU Operator has to be successfully initialised. 
To do so, you need to assure DaemonSet is ready and the Validator Pod has succeeded.

.. note::
   This process can take approximately 5 minutes to complete.

Ensure DaemonSet is ready
~~~~~~~~~~~~~~~~~~~~~~~~~

First, ensure that the DaemonSet for the Operator Validator is created:

.. code-block:: bash

  while ! sudo microk8s.kubectl get ds \
      -n gpu-operator-resources \
      nvidia-operator-validator
  do
    sleep 5
  done

.. note::
   It takes some seconds for the DaemonSet to get created. 
   The above command returns a message like the following at the beginning of the process:
   ``Error from server (NotFound): daemonsets.apps "nvidia-operator-validator" not found``

Once completed, you should expect an output like this:

.. code-block:: text

   Error from server (NotFound): daemonsets.apps "nvidia-operator-validator" not found
   ...
   Error from server (NotFound): daemonsets.apps "nvidia-operator-validator" not found
   NAME                        DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                                   AGE
   nvidia-operator-validator   1         1         0       1            0           nvidia.com/gpu.deploy.operator-validator=true   17s

Ensure the Validator Pod succeeded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, you need to wait for the Validator Pod to succeed:

.. code-block:: bash

   echo "Waiting for the NVIDIA Operator validations to complete..."

   while ! sudo microk8s.kubectl logs \
       -n gpu-operator-resources \
       -l app=nvidia-operator-validator \
       -c nvidia-operator-validator | grep "all validations are successful"
   do
       sleep 5
   done

.. note::
   It takes some seconds for the Validator Pod to get initialised. 
   The above command returns a message like the following at the beginning of the process:
   ``Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-4rq5n" is waiting to start: PodInitializing``

Once completed, you should expect an output like this:

.. code-block:: text

   Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-4rq5n" is waiting to start: PodInitializing
   ...
   Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-4rq5n" is waiting to start: PodInitializing
   all validations are successful

.. _verify_nvidia_operator:

Verify DSS detects the GPU
--------------------------

At this point, the underlying MicroK8s cluster has been configured for handling the NVIDIA GPU.
Verify the DSS CLI has detected the GPU by checking the DSS status as follows:

.. code-block:: bash

  dss status

You should expect an output like this:

.. code-block:: bash

  [INFO] MLflow deployment: Ready
  [INFO] MLflow URL: http://10.152.183.74:5000
  [INFO] GPU acceleration: Enabled (NVIDIA-GeForce-RTX-3070-Ti)

.. note::

  The GPU model `NVIDIA-GeForce-RTX-3070-Ti` might differ from your setup.

See also
--------

* To learn how to manage your DSS environment, check :ref:`manage_DSS`. 
* If you are interested in managing Jupyter Notebooks within your DSS environment, see :ref:`manage_notebooks`.
