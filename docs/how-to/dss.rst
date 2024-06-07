Manage DSS
==========

This guide describes how to manage Data Science Stack (DSS).

Set up DSS
-----------

DSS is a CLI-based product. 
The DSS Command Line Interface (CLI) is distributed as a snap accessible from the `snap store <dss snap store_>`_.

Prerequisites
~~~~~~~~~~~~~

Before proceeding, ensure that you have the following:

- A system with `snap`_ installed.

Install the DSS CLI
~~~~~~~~~~~~~~~~~~~

To install the DSS CLI using snap, run the following command:

.. code-block:: bash

    sudo snap install data-science-stack

Then you can run the DSS CLI by running the following command:

.. code-block:: bash

    dss

Start DSS
---------

This section explains how to initialise the DSS environment through the DSS CLI.

The `dss initialize` command provides a way to initialise the DSS environment. This command:

* stores credentials for the MicroK8s cluster
* allocates storage for all DSS Notebooks to share
* deploys an `MLflow <MLflow Docs_>`_ model registry

Prerequisites
~~~~~~~~~~~~~

Before initializing DSS, ensure you have the following:

- DSS CLI installed on your workstation.
- `MicroK8s`_ installed on your workstation.

Initialise the DSS Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initialise DSS through the `dss initialize` command, for example:

.. code-block:: shell

    dss initialize --kubeconfig "$(sudo microk8s config)"

where we provide the content of our MicroK8s cluster's kubeconfig using the `--kubeconfig` option.

.. note::
   Don't forget the quotes around `$(microk8s config)` - without them, the content may be interpreted by your shell.

The expected output of the above command is:

.. code-block:: none

    [INFO] Executing initialize command
    [INFO] Storing provided kubeconfig to /home/user/.dss/config
    [INFO] Waiting for deployment mlflow in namespace dss to be ready...
    [INFO] Deployment mlflow in namespace dss is ready
    [INFO] DSS initialized. To create your first notebook run the command:

    dss create

    Examples:
      dss create my-notebook --image=pytorch
      dss create my-notebook --image=kubeflownotebookswg/jupyter-scipy:v1.8.0

Remove DSS
----------

This guide explains how to purge (remove) the Data Science Stack (DSS) environment from your MicroK8s cluster
The `dss purge` command provides a way to remove everything deployed by DSS from your MicroK8s cluster. 
This includes all the DSS components, such MLflow and Jupyter Notebooks.

.. note::

    This action removes the components of the DSS environment, but it does not remove the DSS CLI or your MicroK8s cluster.  To remove those, `remove their snaps <https://snapcraft.io/docs/quickstart-tour>`_.

To purge all DSS components from your machine, do:

.. code-block:: bash

    dss purge

This will remove:

* all Jupyter Notebooks
* the MLflow server
* any data stored within the DSS environment

.. caution::

    This action is irreversible. All data stored within the DSS environment will be lost.

The expected output from the above command is:

.. code-block:: none

    [INFO] Waiting for namespace dss to be deleted...
    [INFO] Success: All DSS components and notebooks purged successfully from the Kubernetes cluster.

Get DSS status
--------------

This guide explains how to check the status of your DSS environment.
The `dss status` command provides a quick way to check the status of your DSS environment, including the status of MLflow and whether a GPU is detected in the environment.

To see the status of DSS, run the following command:

.. code-block:: bash

    dss status

If you have a DSS environment running and no GPU available, the expected output is:

.. code-block:: none

    [INFO] MLflow deployment: Ready
    [INFO] MLflow URL: http://10.152.183.68:5000
    [INFO] GPU acceleration: Disabled
