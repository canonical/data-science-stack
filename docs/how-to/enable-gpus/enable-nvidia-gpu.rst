.. _nvidia_gpu:

Enable NVIDIA GPUs
==================

This guide describes how to configure Data Science Stack (DSS) to utilise your NVIDIA GPUs within a Canonical K8s environment.

DSS supports GPU acceleration by leveraging the `NVIDIA GPU Operator`_. The operator ensures that the necessary components, including drivers and runtime, are set up correctly to enable GPU workloads.

Prerequisites
-------------

* DSS is :ref:`installed <install_DSS_CLI>` and :ref:`initialised <initialise_DSS>`.
* Your machine includes an NVIDIA GPU.

.. _install_nvidia_operator:

Install the NVIDIA GPU Operator
-------------------------------

To enable GPU support, you must install the NVIDIA GPU Operator in your Kubernetes cluster. 
Follow `NVIDIA GPU Operator Installation Guide <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html>`_ for installation details.

Verify the NVIDIA Operator is up
--------------------------------

Once the NVIDIA GPU Operator is installed, verify that it has been successfully initialized before running workloads.

Ensure DaemonSet is ready
~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following command to verify that the DaemonSet for the NVIDIA Operator Validator is created:

.. code-block:: bash

   while ! kubectl get ds -n gpu-operator-resources nvidia-operator-validator; do
      sleep 5
   done

.. note::
   It may take a few seconds for the DaemonSet to be created.

Once completed, you should see an output similar to this:

.. code-block:: text

   NAME                        DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                                   AGE
   nvidia-operator-validator   1         1         0       1            0           nvidia.com/gpu.deploy.operator-validator=true   17s

Ensure the Validator Pod succeeded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following command to check if the NVIDIA Operator validation is successful:

.. code-block:: bash

   echo "Waiting for the NVIDIA Operator validations to complete..."

   while ! kubectl logs -n gpu-operator-resources -l app=nvidia-operator-validator -c nvidia-operator-validator | grep "all validations are successful"; do
       sleep 5
   done

.. note::
   If the pod is still initializing, you may see an error like:
   ``Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-xxxx" is waiting to start: PodInitializing``

Once completed, the output should include:

.. code-block:: text

   all validations are successful

Use cases for different driver states
-------------------------------------

The NVIDIA GPU Operator behaves differently depending on whether your system already has an NVIDIA driver installed. Below are the three primary scenarios:

Device with no NVIDIA driver installed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The GPU Operator will **automatically install** the necessary NVIDIA driver.
- This installation process may take longer as it involves setting up drivers and runtime components.
- Once the process is complete, GPU should be detected successfully.

Device with an up-to-date NVIDIA driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The GPU Operator detects the existing driver and proceeds without reinstalling it.
- However, to avoid redundant installations, it is recommended to disable driver installation explicitly when deploying the operator.
- Follow the upstream documentation for the correct configuration to disable driver installation in this case.

Device with an outdated NVIDIA driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- If an older driver version is detected, the operator may attempt to install a newer version.
- This could lead to conflicts if the outdated driver does not match the required CUDA version.
- To prevent issues, update the driver manually or remove the outdated version before deploying the GPU Operator.

.. _verify_nvidia_operator:

Verify DSS detects the GPU
--------------------------

After installing and configuring the NVIDIA GPU Operator, verify that DSS detects the GPU by checking its status:

.. code-block:: bash

   dss status

You should expect an output like this:

.. code-block:: text

   MLflow deployment: Ready
   MLflow URL: http://10.152.183.74:5000
   GPU acceleration: Enabled (NVIDIA-GeForce-RTX-3070-Ti)

.. note::
  The GPU model displayed may differ based on your hardware.

See also
--------

* To learn how to manage your DSS environment, check :ref:`manage_DSS`. 
* If you are interested in managing Jupyter Notebooks within your DSS environment, see :ref:`manage_notebooks`.
