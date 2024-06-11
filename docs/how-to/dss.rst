Manage DSS
==========

This guide describes how to manage Data Science Stack (DSS).

DSS is a Command Line Interface (CLI)-based environment and distributed as a `snap`_.

Install DSS
-----------

.. important::
   To install DSS, ensure that you have previously installed `Snap`_ and `MicroK8s`_.

You can install DSS using `snap` as follows:

.. code-block:: bash

    sudo snap install data-science-stack

Then, you can run the DSS CLI with:

.. code-block:: bash

    dss

Start DSS
---------

You can initialise DSS through `dss initialize`.
This command:

* stores credentials for the MicroK8s cluster.
* allocates storage for your DSS Jupyter Notebooks.
* deploys an `MLflow <MLflow Docs_>`_ model registry.

.. code-block:: shell

    dss initialize --kubeconfig "$(sudo microk8s config)"

The `--kubeconfig` option is used to provide your MicroK8s cluster's kubeconfig.

.. note::
   Note the use of quotes for the `--kubeconfig` option. Without them, the content may be interpreted by your shell.

You should expect an output like this:

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

You can remove DSS from your MicroK8s cluster through `dss purge`. 
This command purges all the DSS components, including:

* All Jupyter Notebooks.
* The MLflow server.
* Any data stored within the DSS environment.

.. note::

    This action removes the components of the DSS environment, but it does not remove the DSS CLI or your MicroK8s cluster.  
    To remove those, `delete their snaps <https://snapcraft.io/docs/quickstart-tour>`_.

.. code-block:: bash

    dss purge

.. caution::

    This action is irreversible. All data stored within the DSS environment will be lost.

You should expect an output like this:

.. code-block:: none

    [INFO] Waiting for namespace dss to be deleted...
    [INFO] Success: All DSS components and notebooks purged successfully from the Kubernetes cluster.

Get DSS status
--------------

You can check the DSS status through `dss status`. 
This command provides a quick way to check the status of your DSS environment, including the MLflow status and whether a GPU is detected in your environment.

.. code-block:: bash

    dss status

If you already have a DSS environment running and no GPU available, the expected output is:

.. code-block:: none

    [INFO] MLflow deployment: Ready
    [INFO] MLflow URL: http://10.152.183.68:5000
    [INFO] GPU acceleration: Disabled

See also
--------

To learn how to manage your Jupyter Notebooks, check :doc:`jupyter-notebook`. If you are interested in managing MLflow within your DSS environment, see :doc:`mlflow`.