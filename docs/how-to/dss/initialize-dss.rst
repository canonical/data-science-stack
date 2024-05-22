Initialize DSS
==============

This guide explains how to initialize the DSS environment through the Data Science Stack (DSS) Command Line Interface (CLI).

Overview
--------

The `dss initialize` command provides a way to initialize the DSS environment. This command:

* stores credentials for the MicroK8s cluster
* allocates storage for all DSS Notebooks to share
* deploys an `MLflow <MLflow Docs_>`_ model registry

Prerequisites
-------------

Before initializing DSS, ensure you have the following:

- DSS CLI installed on your workstation.
- `MicroK8s`_ installed on your workstation.

Initializing the DSS Environment
--------------------------------

Initialize DSS through the `dss initialize` command, for example:

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

From this point, DSS is ready for you to :doc:`create your first notebook </how-to/jupyter-notebook/create-notebook>`.

Conclusion
----------

This guide explained how to initialize the DSS environment through the DSS CLI. You can now proceed to :doc:`create your first notebook </how-to/jupyter-notebook/create-notebook>`.
