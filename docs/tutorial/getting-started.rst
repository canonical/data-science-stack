.. _tutorial:

Getting Started
===============

This guide will walk you through how you can get started with the Data
Science Stack. From setting up MicroK8s in your host environment and
configuring GPU drivers, all the way to running your first notebook.

Prerequisites
^^^^^^^^^^^^^

* Ubuntu 22.04
* An internet connection
* DSS relies on MicroK8s, that requires as little as 540MB of memory.
  But to accommodate workloads, we recommend a system with at least 20G
  of disk space and 4G of memory.

Setting up MicroK8s
^^^^^^^^^^^^^^^^^^^

The DSS relies on a container orchestration system, that can also take
care of exposing the host GPUs to the workloads. In this case we will use
MicroK8s snap, which gets installed on the host machine.

All the workloads and state managed by DSS will be running on top of
MicroK8s.

You can install MicroK8s with the following commands:

.. code-block:: bash

   sudo snap install microk8s --channel 1.28/stable --classic
   microk8s enable storage dns rbac

For further information on how to get started with MicroK8s, you can
follow `MicroK8s' Getting Started`_ page.

(Optional) Setup NVIDIA drivers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following are optional for machines that contain NVIDIA GPUs. To ensure
the DSS can utilise the NVIDIA GPUs:

1. The host will need to have the NVIDIA drivers installed
2. MicroK8s will need to be setup to utilise those drivers

MicroK8s is leveraging the `NVIDIA Operator`_ to for setting up and
configuring the NVIDIA runtime. The NVIDIA Operator will also install
the NVIDIA drivers, if they are not present already on the host machine.

To enable the NVIDIA runtimes on MicroK8s you need to run the following
command:

.. code-block:: bash

   microk8s enable gpu


.. note::
   The NVIDIA Operator will detect if the NVIDIA drivers are not present at all
   and will install them in this case. But the NVIDIA Operator can also detect
   if you have drivers already installed. In this case the NVIDIA Operator will
   use the host's drivers.


Install the DSS CLI
^^^^^^^^^^^^^^^^^^^

At this point we've installed MicroK8s and configured it to use the host's
NVIDIA GPU. The next step now is to install the DSS CLI snap.

You can install the CLI with the following commands:

.. code-block:: bash

   sudo snap install data-science-stack --channel latest/stable

Initialise the DSS
^^^^^^^^^^^^^^^^^^

Now that you have the DSS CLI installed the next step is to initialise
the DSS on top of MicroK8s.

Under the hood this will create a K8s namespace and prepare the namespace
accordingly, by installing MLflow and setting up the shared storage for the
Notebooks that will be launched in the future.

You can initialise the DSS with the following commands:

.. code-block:: bash

   dss initialize --kubeconfig="$(microk8s kubeconfig)"

Launch a Notebook
^^^^^^^^^^^^^^^^^

At this point the DSS is setup on the host and you are ready to start
managing containerised Notebook environments. You can use the DSS CLI
now to launch containerised Notebook environments and access JupyterLab.

You can start your first Notebook with the following command:

.. code-block:: bash

   dss create my-tensorflow-notebook --image=kubeflownotebookswg/jupyter-tensorflow-cuda:v1.8.0

Once the command succeeds it will also return a URL that can be used
to connect to the JupyterLab UI of that Notebook.
For example you should see output like this:

.. code-block:: none

   [INFO] Executing create command
   [INFO] Waiting for deployment my-tensorflow-notebook in namespace dss to be ready...
   [INFO] Deployment my-tensorflow-notebook in namespace dss is ready
   [INFO] Success: Notebook my-tensorflow-notebook created successfully.
   [INFO] Access the notebook at http://10.152.183.42:80.

Next Steps
^^^^^^^^^^

* Want to learn how to interact with your Notebooks? Try :ref:`jupyter-notebooks`
* Want to learn more about handling data? See :ref:`access-data`
* Want to connect to MLflow? See :ref:`notebook-mlflow`
