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
* 50GB of disk space is recommended. This includes the `requirements <https://microk8s.io/docs/getting-started>`_ for MicroK8s.

.. _set_microk8s:

Setting up MicroK8s
-------------------

DSS relies on a container orchestration system, capable of exposing the host GPUs to the workloads. 
`MicroK8s`_ is used as the orchestration system.
All the workloads and state managed by DSS are running on top of MicroK8s.

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
   ``Waiting for deployment mlflow in namespace dss to be ready...``

Once initialised, you should see an output like this:

.. code-block:: none

   Deployment mlflow in namespace dss is ready
   
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

   Executing create command
   Waiting for deployment my-tensorflow-notebook in namespace dss to be ready...
   Deployment my-tensorflow-notebook in namespace dss is ready
   Success: Notebook my-tensorflow-notebook created successfully.
   Access the notebook at http://10.152.183.42:80.

Once you know the URL, open a web browser and enter the URL into the address bar. 
This will direct you to the notebook UI where you can start working with your notebook.

Next Steps
----------
* To learn more about how to interact with DSS, see :ref:`manage_DSS`.
* To learn about handling data, check out :ref:`access-data`.
* To connect to MLflow, see :ref:`manage_MLflow`.
* To leverage your GPUs, see :doc:`Enable GPUs <../how-to/enable-gpus/index>`.
