.. _tutorial:

Getting Started
===============

This guide describes how you can get started with Data Science Stack (DSS). 
From setting up MicroK8s in your host environment, all the way to running your first notebook.

Data Science Stack is a ready-made environment that makes it seamless to run GPU-enabled containerised Machine Learning (ML) environments. 
It provides easy access to a solution for developing and optimising ML models, utilising your machine's GPUs and allowing users to utilise different ML environment images based on their needs.

Prerequisites
-------------

* Ubuntu 22.04 LTS.
* An Internet connection.
* `Snap`_ installed.

.. _set_microk8s:

Setting up MicroK8s
-------------------

DSS relies on a container orchestration system, capable of exposing the host GPUs to the workloads. 
`MicroK8s`_ is used as the orchestration system.
All the workloads and state managed by DSS will be running on top of MicroK8s.

.. note::

   `MicroK8s requires <https://microk8s.io/docs/getting-started>`_ 540MB of memory.
   To better accommodate workloads, a system with at least 20G of disk space and 4G of memory is recommended.

You can install MicroK8s using ``snap`` as follows:

.. code-block:: bash

   sudo snap install microk8s --channel 1.28/stable --classic
   sudo microk8s enable hostpath-storage
   sudo microk8s enable dns
   sudo microk8s enable rbac

.. _install_DSS_CLI:

Install the DSS CLI
-------------------

DSS is a Command Line Interface (CLI)-based environment.
Now, install the DSS CLI using the following command:

.. code-block:: bash

   sudo snap install data-science-stack --channel latest/stable

.. _initialise_DSS:

Initialise DSS
--------------

Next, you need to initialise DSS on top of MicroK8s and prepare MLflow:

.. code-block:: bash

   dss initialize --kubeconfig="$(sudo microk8s config)"

.. note::

   The initialisation might take a few minutes to complete.
   While the process is in progress, you will see the following message:
   ``[INFO] Waiting for deployment my-tensorflow-notebook in namespace dss to be ready...``
   
Launch a Notebook
-----------------

At this point, DSS is set up and you are ready to start managing containerised notebook environments. 
You can use the DSS CLI to launch and access them using JupyterLab.

Start your first Jupyter Notebook with the following command:

.. code-block:: bash

   dss create my-tensorflow-notebook --image=kubeflownotebookswg/jupyter-tensorflow-cuda:v1.8.0

Once the command succeeds, it returns a URL that can be used to connect to the JupyterLab User Interface (UI) of that notebook.
For example, you should expect an output like this:

.. code-block:: none

   [INFO] Executing create command
   [INFO] Waiting for deployment my-tensorflow-notebook in namespace dss to be ready...
   [INFO] Deployment my-tensorflow-notebook in namespace dss is ready
   [INFO] Success: Notebook my-tensorflow-notebook created successfully.
   [INFO] Access the notebook at http://10.152.183.42:80.

Once you know the URL, open a web browser and enter the URL into the address bar. 
This will direct you to the notebook UI where you can start working with your notebook.

Next Steps
----------
* To learn more about how to interact with DSS, see :ref:`manage_DSS`.
* To learn about handling data, check out :ref:`access-data`.
* To connect to MLflow, see :ref:`manage_MLflow`.
* To enable your NVIDIA GPUs, check out :ref:`nvidia_gpu`.
