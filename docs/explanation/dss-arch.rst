DSS architecture
================

This guide provides an overview of the Data Science Stack (DSS) architecture, its main components, and their interactions. 

DSS is a ready-to-run environment for Machine Learning (ML) and Data Science (DS). 
It's built on open-source tooling, including `Canonical K8s`_, JupyterLab, and `MLflow <https://ubuntu.com/blog/what-is-mlflow>`_.

DSS is distributed as a `snap`_ and usable on any Ubuntu workstation. 
This provides robust security management and user-friendly version control, enabling seamless updates and auto-rollback in case of failure. 

Using DSS, you can perform the following tasks: 

* Installing and managing the DSS Python library.
* Deploying and managing Jupyter Notebooks.
* Deploying and managing MLflow.
* Running GPU workloads.

Architecture overview
---------------------

The DSS architecture can be thought of as a stack of layers. 
These layers, from top to bottom, include:

* :ref:`Application <app_layer>`.
* :ref:`ML tools <ml_tools>`.
* :ref:`Orchestration <orch_layer>`.
* :ref:`Operating system (OS) <os_layer>`.

The following diagram showcases it:

.. figure:: https://assets.ubuntu.com/v1/1cd21eb3-dss_arch.png
   :width: 600px
   :alt: text

   Architecture overview

More details on each layer are discussed in the following sections.

.. _app_layer:

Application
~~~~~~~~~~~

DSS is a Command Line Interface (CLI)-based tool, accessible from the Ubuntu terminal. 
See :ref:`manage_DSS` to learn about how to manage your DSS environment and the available CLI commands.

.. _ml_tools:

ML tools
~~~~~~~~

DSS includes:

* Jupyter Notebooks: Open-source environment that provides a flexible interface to organise DS projects and ML workloads. 
* MLflow: Open-source platform for managing the ML life cycle, including experiment tracking and model registry.
* ML frameworks: DSS comes by default with PyTorch and TensorFlow. Users can manually add other frameworks, depending on their needs and use cases.

Jupyter Notebooks
^^^^^^^^^^^^^^^^^

A `Jupyter Notebook <Jupyter Notebooks_>`_ is essentially a `Kubernetes deployment <Pod_>`_, also known as `Pod`, running a Docker image with Jupyter Lab and a dedicated ML framework, such as PyTorch or TensorFlow.
For each Jupyter Notebook, DSS mounts a `Hostpath <Microk8s hostpath docs_>`_ directory-backed persistent volume to the data directory. 
All Jupyter Notebooks share the same persistent volume, allowing them to exchange data seamlessly. 
The full path to that persistent volume is `/home/jovyan/shared`.

MLflow
^^^^^^

`MLflow <https://ubuntu.com/blog/what-is-mlflow>`_ operates in `local mode <https://mlflow.org/docs/latest/tracking/#other-tracking-setup>`_, 
meaning that metadata and artefacts are, by default, stored in a local directory.

This local directory is backed by a persistent volume, mounted to a Hostpath directory of the MLflow Pod.
The persistent volume can be found in the directory `/mlruns`.

.. _orch_layer:

Orchestration
~~~~~~~~~~~~~

DSS requires a container orchestration solution. 
DSS relies on `Canonical K8s`_, a lightweight Kubernetes distribution.

Therefore, Canonical K8s needs to be deployed before installing DSS on the host machine. 
It must be configured with local storage support to handle persistent volumes used by DSS.

.. _gpu_support:

GPU support
^^^^^^^^^^^

DSS can run with or without the use of GPUs.
If needed, the NVIDIA GPU Operator should be deployed following the official documentation: 
`NVIDIA GPU Operator <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html>`_.

DSS does not automatically install the tools and libraries required for running GPU workloads.
It relies on Canonical K8s for the required operating-system drivers.
It also depends on the chosen image, for example, CUDA when working with NVIDIA GPUs.

.. caution::
   GPUs from other silicon vendors rather than NVIDIA can be configured. However, its functionality is not guaranteed.
 
Storage
^^^^^^^

DSS expects a default `storage class <https://kubernetes.io/docs/concepts/storage/storage-classes/>`_ in the Kubernetes deployment, which is used to persist Jupyter Notebooks and MLflow artefacts.   
In Canonical K8s, a local storage class should be configured to provision Kubernetes' *PersistentVolumeClaims* (`PVCs <https://kubernetes.io/docs/concepts/storage/persistent-volumes/>`_). 

A shared PVC is used across all Jupyter Notebooks to share and persist data. 
MLflow also uses its dedicated PVC to store the logged artefacts.
This is the DSS default storage configuration and cannot be altered.

This choice ensures that all storage is backed up on the host machine in the event of cluster restarts.

.. note::
   By default, you can access the DSS storage anytime under your local directory `/var/snap/k8s/common/default-storage`. 

The following diagram summarises the DSS storage:

.. figure:: https://assets.ubuntu.com/v1/2130fd66-dss_storage.png
   :width: 800px
   :alt: text

   Storage overview

.. _os_layer:

Operating system
~~~~~~~~~~~~~~~~

DSS is native on Ubuntu, being developed, tested, and validated on it. 
Moreover, the solution can be used on any Linux distribution.

Namespace configuration
-----------------------

DSS runs on a dedicated Kubernetes namespace. 
By default, it contains two Kubernetes Pods. 

The NVIDIA GPU support runs on another dedicated namespace. 
This includes the GPU Operator for managing access and usage.

Accessibility
-------------

Jupyter Notebooks and MLflow can be accessed from a web browser through the Pod IP that is given access through Canonical K8s.
See :ref:`access_notebook` and :ref:`access_mlflow` for more details.

.. _Canonical K8s: https://snapcraft.io/k8s
