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
   :width: 600px
   :alt: text

   Architecture overview

.. _app_layer:

Application
~~~~~~~~~~~

At the application layer, DSS includes:

* Jupyter Notebook: Open source environment that provides a flexible interface to organise DS projects and ML workloads. 
* MLflow: Open source platform for managing ML life cycle, including experiment tracking and model registry.
* ML frameworks: DSS comes by default with PyTorch and Tensorflow. Users can manually add other frameworks, depending on their needs and use cases.

Jupyter Notebooks
^^^^^^^^^^^^^^^^^

A Jupyter Notebook is essentially a Kubernetes deployment, also known as `Pod`, running a Docker image with Jupyter Lab and a dedicated ML framework, such as Pytorch or Tensorflow.
For each Jupyter Notebook, DSS mounts a host path directory-backed persistent volume to the data directory. 
All Jupyter Notebooks share the same persistent volume, allowing them to exchange data seamlessly. 

MLflow
^^^^^^

MLflow operates in local mode, meaning that metadata and artefacts for each run are, by default, recorded to a local directory named `mlruns`. 
This directory is backed by a persistent volume, mounted to a host path directory of the MLflow Kubernetes deployment.

.. _container_layer:

Containerisation
~~~~~~~~~~~~~~~~

DSS needs a container orchestration solution. 
DSS relies on MicroK8s, a lightweight Kubernetes distribution.

Therefore, MicroK8s needs to be deployed before installing DSS on the host machine. 
It must be configured with the storage add-on. 
This is required to use host path storage in the cluster. 

DSS can run with or without the use of GPUs.
If :ref:`gpu_support` is needed, MicroK8s can be configured with the desired GPU add-on. 

.. _gpu_support:

GPU support
^^^^^^^^^^^

DSS does not automatically install the tools and libraries required for running GPU workloads.
To do so, it relies on MicroK8s, or any other Kubernetes deployment used as the orchestration solution.

DSS is designed to support the deployment of containerised GPU workloads on NVIDIA GPUs. 
MicroK8s simplifies the GPU access and usage through the NVIDIA GPU operator. 

.. caution::
   GPUs from other silicon vendors rather than NVIDIA can be configured. However, its functionality is not guaranteed.
 
Storage
^^^^^^^

DSS expects a default storage class in the Kubernetes deployment, which is used to persist Jupyter Notebooks and MLflow artefacts.   
In MicroK8s, the storage add-on is used, providing the host path storage option for Kubernetes' *PersistentVolumeClaims* (PVCs). 

A shared PVC is used across all Jupyter Notebooks to share and persist data. 
MLflow also uses its dedicated PVC to store the logged artefacts.

This choice ensures that all storage is backed up on the host machine in the event of MicroK8s restarts.

.. note::
   By default, users can access this storage anytime under `/var/snap/microk8s/common/default-storage`. 

The following diagram summarises the DSS storage:

.. figure:: https://assets.ubuntu.com/v1/299750d3-dss_storage.png
   :width: 800px
   :alt: text

   Storage overview

.. _os_layer:

Operating system
~~~~~~~~~~~~~~~~

DSS is native on Ubuntu, being developed, tested and validated on it. 

Moreover, the solution can be used on any Linux distribution, Windows through Windows Subsystem Linux (WSL) or MacOS through Multipass, 
but the GPU support is at risk, depending on the GPU operator. 


