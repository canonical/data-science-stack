DSS architecture
================

This guide provides an overview of the DSS architecture, its main components and their interactions. 

Data science stack (DSS) is a ready-to-run environment for Machine Learning (ML) and Data Science (DS). 
It's built on open-source tooling, including `MicroK8s`_, JupyterLab and `MLflow <https://ubuntu.com/blog/what-is-mlflow>`_, and usable on any Ubuntu / `snap`_-enabled workstation.

Architecture overview
---------------------

DSS is a Command Line Interface (CLI)-based tool, accessible from the Ubuntu terminal. 
See :ref:`manage_DSS` to learn about how to manage your DSS environment and the available commands.

DSS is distributed as a `snap`_. 
This provides robust security management and user-friendly version control, enabling seamless updates and auto-rollback in case of failure. 

Using DSS, you can perform the following tasks: 

* Installing and managing the DSS Python library.
* Deploying and managing Jupyter Notebooks.
* Deploying and managing MLflow.

The DSS architecture involves three high-level layers:

* :ref:`Application <app_layer>`.
* :ref:`Containerisation <container_layer>`. 
* :ref:`Operating system <os_layer>`.

The following diagram showcases it:

.. figure:: https://assets.ubuntu.com/v1/297b97d4-dss_arch.png
   :width: 600px
   :alt: text

   Architecture overview

The DSS square represents the application layer, MicroK8s provides the orchestration layer, and Ubuntu is the native operating system for DSS.
More details on each layer are discussed in the following sections.

.. _app_layer:

Application
~~~~~~~~~~~

At the application layer, DSS includes:

* Jupyter Notebooks: Open source environment that provides a flexible interface to organise DS projects and ML workloads. 
* MLflow: Open source platform for managing ML life cycle, including experiment tracking and model registry.
* ML frameworks: DSS comes by default with PyTorch and Tensorflow. Users can manually add other frameworks, depending on their needs and use cases.

Jupyter Notebooks
^^^^^^^^^^^^^^^^^

A `Jupyter Notebook <Jupyter Notebooks_>`_ is essentially a `Kubernetes deployment <Pod_>`_, also known as `Pod`, running a Docker image with Jupyter Lab and a dedicated ML framework, such as Pytorch or Tensorflow.
For each Jupyter Notebook, DSS mounts a `Hostpath <Microk8s hostpath docs_>`_ directory-backed persistent volume to the data directory. 
All Jupyter Notebooks share the same persistent volume, allowing them to exchange data seamlessly. 

MLflow
^^^^^^

MLflow operates in `local mode <https://mlflow.org/docs/latest/tracking.html#other-configuration-with-mlflow-tracking-server>`_, meaning that metadata and artefacts for each run are, by default, recorded to a local directory named `mlruns`. 
This directory is backed by a persistent volume, mounted to a Hostpath directory of the MLflow Kubernetes deployment.

.. _container_layer:

Containerisation
~~~~~~~~~~~~~~~~

DSS needs a container orchestration solution. 
DSS relies on MicroK8s, a lightweight Kubernetes distribution.

Therefore, MicroK8s needs to be deployed before installing DSS on the host machine. 
It must be configured with the storage add-on. 
This is required to use Hostpath storage in the cluster. 

DSS can run with or without the use of GPUs.
If :ref:`gpu_support` is needed, MicroK8s can be configured with the desired `GPU add-on <https://microk8s.io/docs/addon-gpu>`_. 

.. _gpu_support:

GPU support
^^^^^^^^^^^

DSS does not automatically install the tools and libraries required for running GPU workloads.
To do so, it relies on MicroK8s, or any other Kubernetes deployment used as the orchestration solution.

DSS is designed to support the deployment of containerised GPU workloads on NVIDIA GPUs. 
MicroK8s simplifies the GPU access and usage through the `NVIDIA GPU Operator <NVIDIA Operator_>`_. 

.. caution::
   GPUs from other silicon vendors rather than NVIDIA can be configured. However, its functionality is not guaranteed.
 
Storage
^^^^^^^

DSS expects a default `storage class <https://kubernetes.io/docs/concepts/storage/storage-classes/>`_ in the Kubernetes deployment, which is used to persist Jupyter Notebooks and MLflow artefacts.   
In MicroK8s, the Hostpath storage add-on is chosen, used to provision Kubernetes' *PersistentVolumeClaims* (`PVCs <https://kubernetes.io/docs/concepts/storage/persistent-volumes/>`_). 

A shared PVC is used across all Jupyter Notebooks to share and persist data. 
MLflow also uses its dedicated PVC to store the logged artefacts.
This is the DSS default storage configuration and cannot be altered.

This choice ensures that all storage is backed up on the host machine in the event of MicroK8s restarts.

.. note::
   By default, users can access this storage anytime under `/var/snap/microk8s/common/default-storage`. 

The following diagram summarises the DSS storage:

.. figure:: https://assets.ubuntu.com/v1/2130fd66-dss_storage.png
   :width: 800px
   :alt: text

   Storage overview

.. _os_layer:

Operating system
~~~~~~~~~~~~~~~~

DSS is native on Ubuntu, being developed, tested and validated on it. 

Moreover, the solution can be used on any Linux distribution, Windows through Windows Subsystem Linux (WSL) or MacOS through Multipass, 
but the GPU support is at risk, depending on the GPU operator. 

Namespace configuration
-----------------------

DSS has a dedicated namespace running on MicroK8s. 
By default, it has two Kubernetes pods, but users can add new pods or attach new ML frameworks to the existing ones. 

The NVIDIA GPU support runs on a dedicated namespace. 
This includes the GPU Operator for managing access and usage, together with the `Network Operator <https://docs.nvidia.com/networking/display/cokan10/network+operator>`_, for managing networking components and enabling fast networking. 

.. figure:: https://assets.ubuntu.com/v1/d28ea080-dss_namespace_config.png
   :width: 800px
   :alt: text

   Namespace configuration

Namespaces and all associated data can be managed using the DSS CLI.
See :ref:`manage_DSS` for more details.


Accessibility
-------------

Jupyter Notebooks and MLflow are accessed from a web browser through the pod IP that is given access through MicroK8s.
See :ref:`access_notebook` and :ref:`access_mlflow` for more details.



