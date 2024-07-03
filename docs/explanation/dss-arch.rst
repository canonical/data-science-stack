DSS architecture
================

This guide provides an overview of the DSS architecture, its main components and their interactions. 

Data science stack (DSS) is a ready-to-run environment for Machine Learning (ML) and Data Science (DS). 
It's built on open-source tooling, including MicroK8s, JupyterLab and MLflow, and usable on any Ubuntu/Snap-enabled workstation.

Architecture overview
---------------------

DSS is a Command Line Interface (CLI)-based tool, distributed as a `snap`_, and accessible from the Ubuntu terminal. 
See :ref:`manage_DSS` to learn about how to manage your DSS environment and the available commands.

Using DSS, you can perform the following tasks: 

* Installing and managing the DSS Python library.
* Deploying and managing Jupyter Notebooks.
* Deploying and managing MLflow.

The DSS architecture involves three high-level layers:

* :ref:`Application <app_layer>`.
* :ref:`Containerisation <container_layer>`. 
* :ref:`Operating system <os_layer>`.

The following diagram showcases it:

.. figure:: https://assets.ubuntu.com/v1/617450b0-dss_arch.png
   :width: 700px
   :alt: text

   Architecture overview

.. _app_layer:

Application
~~~~~~~~~~~

At the application layer, DSS includes:

* Jupyter Notebook: Open source environment that provides a flexible interface to organise DS projects and ML workloads. 
* MLflow: Open source platform for managing ML lifecycle, including experiment tracking and model registry.
* ML frameworks: DSS comes by default with PyTorch and Tensorflow. Users can manually add other frameworks, depending on their needs and use cases.

Jupyter Notebooks
^^^^^^^^^^^^^^^^^

A Jupyter Notebook is essentially a Kubernetes deployment, also known as `Pod`, running a Docker image with Jupyter Lab and a dedicated ML framework, such as `scikit-learn`, `Tensorflow` or `Pytorch`. 
For each Jupyter Notebook, DSS mounts a host path directory-backed persistent volume to the data directory. 
All Jupyter Notebooks share the same persistent volume, allowing them to exchange data seamlessly. 

MLflow
^^^^^^

MLflow operates in local mode, meaning that metadata and artefacts for each run are, by default, recorded to a local directory named `mlruns`. 
This directory is backed by a persistent volume, mounted to a host path directory of the MLflow's Kubernetes deployment.

.. _container_layer:

Containerisation
~~~~~~~~~~~~~~~~

DSS needs a container orchestration solution. 
DSS relies on MicroK8s, a lightweight Kubernetes distribution.

Therefore, MicroK8s needs to be deployed before installing DSS on the host machine. 
It must be configured with the storage add-on. 
This is required to use `HostPath`` storage in the cluster. 

If :ref:`gpu_support` is needed, MicroK8s can be configured with the desired GPU add-on. 
In the case of machines with no GPU, DSS will run normally, but the time needed for training will take longer. 

.. _gpu_support:

GPU support
^^^^^^^^^^^

The DSS snap does not include the installation of tools and libraries required for running GPU workloads but it will rely on the MicroK8s snap (or any other Kubernetes deployment) for their installation if needed. DSS is designed to support the deployment of containerised GPU workloads on NVIDIA GPUs. 
In order to enable the GPU, MicroK8s need to be configured following the guidance above.

MicroK8s simplifies the GPU access and usage through the NVIDIA GPU operator. 
For workstations with GPUs from other silicon vendors, you should look into the documentation of the provider and try to enable it. However, its functionality is not guaranteed. 

.. _os_layer:

Operating system
~~~~~~~~~~~~~~~~

