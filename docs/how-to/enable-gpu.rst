.. _nvidia-gpu:

Enable NVIDIA GPUs
==================

This guide describes how to configure DSS to utilise your NVIDIA GPUs.
You can do so by configuring the underlying MicroK8s, on which DSS relies on for running the containerised workloads.

Prerequisites
^^^^^^^^^^^^^

* Have run the :ref:`tutorial` tutorial

Install the NVIDIA Operator
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To ensure DSS can utilise NVIDIA GPUs:

1. The NVIDIA drivers must be installed.
2. MicroK8s must be set up to utilise NVIDIA drivers.

MicroK8s is leveraging the `NVIDIA Operator`_ for setting up and
configuring the NVIDIA runtime. The NVIDIA Operator also installs
the NVIDIA drivers, if they are not present already on your machine.

To enable the NVIDIA runtimes on MicroK8s, run the following command:

.. code-block:: bash

   sudo microk8s enable gpu

.. note::
   The NVIDIA Operator will detect if the NVIDIA drivers are not present at all
   and installs them in this case. Otherwise, it uses the installed drivers.

Verify the NVIDIA Operator is up
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before spinning up workloads, you need to ensure the GPU Operator has
been successfully initialized. This process involved ensuring DaemonSet is ready
and the Validator Pod has succeeded. This can take around 5 minutes.

Ensure DaemonSet is Ready
"""""""""""""""""""""""""

First, ensure that the DaemonSet for the Operator Validator is created:


.. code-block:: bash

  while ! sudo microk8s.kubectl get ds -n gpu-operator-resources nvidia-operator-validator
  do
    sleep 5
  done

.. note::
   It will take some seconds for the DaemonSet to get created. The above command will
   return a message like the following at the beginning:
   ``Error from server (NotFound): daemonsets.apps "nvidia-operator-validator" not found``

The expected output should be:

.. code-block:: text

   Error from server (NotFound): daemonsets.apps "nvidia-operator-validator" not found
   ...
   Error from server (NotFound): daemonsets.apps "nvidia-operator-validator" not found
   NAME                        DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                                   AGE
   nvidia-operator-validator   1         1         0       1            0           nvidia.com/gpu.deploy.operator-validator=true   17s

Ensure the Validator succeeded
""""""""""""""""""""""""""""""

Next we'll need to wait for the Validator Pod to succeed:

.. code-block:: bash

  echo "Waiting for the NVIDIA Operator validations to complete..."
  while ! sudo microk8s.kubectl logs -n gpu-operator-resources -l app=nvidia-operator-validator -c nvidia-operator-validator | grep "all validations are successful"
  do
    sleep 5
  done

.. note::
   It will take some seconds for the Pod to get initialized . The above command will
   return a message like the following at the beginning:
   ``Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-4rq5n" is waiting to start: PodInitializing``

The expected output should be:

.. code-block:: text

   Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-4rq5n" is waiting to start: PodInitializing
   ...
   Error from server (BadRequest): container "nvidia-operator-validator" in pod "nvidia-operator-validator-4rq5n" is waiting to start: PodInitializing
   all validations are successful

Verify the DSS detects the GPU
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  dss status

Expected output:

.. code-block:: bash

  [INFO] MLflow deployment: Ready
  [INFO] MLflow URL: http://10.152.183.74:5000
  [INFO] GPU acceleration: Enabled (NVIDIA-GeForce-RTX-3070-Ti)

.. note::

  The GPU model `NVIDIA-GeForce-RTX-3070-Ti` will be different depending on your device.

Launch GPU-enabled Notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^^

At this point the DSS is fully configured to utilise the host's GPU. The next step will
be to deploy a notebook that also contains CUDA runtimes, alongside with ML frameworks
that can utilise the GPU.

You can find a list of proposed images that include CUDA with the following command:

.. code-block:: bash

   dss create --help | grep cuda

You should see an output similar to this one:

.. code-block:: bash

        - pytorch-cuda = kubeflownotebookswg/jupyter-pytorch-cuda-full:v1.8.0
        - tensorflow-cuda = kubeflownotebookswg/jupyter-tensorflow-cuda-full:v1.8.0

Pick one of the two images and create a notebooks with:

.. code-block:: bash

   dss create my-notebook --image=tensorflow-cuda


To confirm the GPU is detected and usable you can run the following python code snippet

.. code-block:: python

   import tensorflow as tf

   tf.config.list_physical_devices('GPU')
