.. _tutorial:

Getting Started
===============

This guide will walk you through how you can get started with the Data
Science Stack. From setting up MicroK8s in your host environment and
configuring GPU drivers, all the way to running your first notebook.

Overview
^^^^^^^^
The Data Science Stack (DSS) is a ready-made environment that makes it seamless to run GPU enabled containerized Machine Learning (ML) environments. It provides easy access to a solution for developing and optimising ML models, utilising the machine's GPUs and allowing users to utilise different ML environment images based on their needs.

Prerequisites
^^^^^^^^^^^^^

* Ubuntu 22.04
* An internet connection
* DSS relies on `MicroK8s`_, that requires as little as 540MB of memory.
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
   sudo microk8s enable storage dns rbac

Install the DSS CLI
^^^^^^^^^^^^^^^^^^^

At this point we've installed MicroK8s and configured it to use the host's
NVIDIA GPU. The next step now is to install the DSS CLI snap.

You can install the CLI with the following command:

.. code-block:: bash

   sudo snap install data-science-stack --channel latest/stable

Initialise the DSS
^^^^^^^^^^^^^^^^^^

Now that you have the DSS CLI installed the next step is to initialise
the DSS on top of MicroK8s and prepare MLflow.

You can initialise the DSS with the following command:

.. code-block:: bash

   dss initialize --kubeconfig="$(sudo microk8s config)"

.. note::
   The `dss initialize` command might take a few minutes to complete.
   
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
* Want to utilise the NVIDIA GPUs in your machine? See :ref:`setup-nvidia-drivers`
* Want to learn how to interact with your Notebooks? Try :ref:`jupyter-notebooks`
* Want to learn more about handling data? See :ref:`access-data`
* Want to connect to MLflow? See :ref:`notebook-mlflow`
