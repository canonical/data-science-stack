.. _tutorial:

Getting Started
===============

This guide describes how you can get started with Data Science Stack (DSS). 
From setting up MicroK8s in your host environment and configuring GPU drivers, all the way to running your first notebook.

Data Science Stack is a ready-made environment that makes it seamless to run GPU-enabled containerised Machine Learning (ML) environments. 
It provides easy access to a solution for developing and optimising ML models, utilising your machine's GPUs and allowing users to utilise different ML environment images based on their needs.

Prerequisites
^^^^^^^^^^^^^

* Ubuntu 22.04
* An Internet connection
* DSS relies on `MicroK8s`_, that requires as little as 540MB of memory.
  But to accommodate workloads, we recommend a system with at least 20G
  of disk space and 4G of memory.

.. _set_microk8s:

Setting up MicroK8s
^^^^^^^^^^^^^^^^^^^

DSS relies on a container orchestration system, capable of exposing the host GPUs to the workloads. 
In this tutorial, MicroK8s is used as the orchestration system.
All the workloads and state managed by DSS will be running on top of MicroK8s.

You can install MicroK8s using `snap`_ as follows:

.. code-block:: bash

   sudo snap install microk8s --channel 1.28/stable --classic
   sudo microk8s enable storage dns rbac

.. _install_DSS_CLI:

Install the DSS CLI
^^^^^^^^^^^^^^^^^^^

Now, install the DSS CLI using the following command:

.. code-block:: bash

   sudo snap install data-science-stack --channel latest/stable

.. _initialise_DSS:

Initialise the DSS
^^^^^^^^^^^^^^^^^^

Next, you need to initialise DSS on top of MicroK8s and prepare MLflow:

.. code-block:: bash

   dss initialize --kubeconfig="$(sudo microk8s config)"

.. note::
   The `dss initialize` command might take a few minutes to complete.
   
Launch a Notebook
^^^^^^^^^^^^^^^^^

At this point, DSS is set up and you are ready to start managing containerised Notebook environments. 
You can use the DSS CLI now to launch containerised Notebook environments and access JupyterLab.

Start your first Notebook with the following command:

.. code-block:: bash

   dss create my-tensorflow-notebook --image=kubeflownotebookswg/jupyter-tensorflow-cuda:v1.8.0

Once the command succeeds, it returns a URL that can be used to connect to the JupyterLab UI of that Notebook.
For example, you should expect an output like this:

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
