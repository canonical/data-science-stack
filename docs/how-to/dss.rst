.. _manage_DSS:

Manage DSS
==========

This guide describes how to manage Data Science Stack (DSS).

DSS is a Command Line Interface (CLI)-based environment and distributed as a `snap`_.

Install
-------

.. note::
   To install DSS, ensure you have previously installed `Snap`_ and `Canonical K8s`_.

You can install DSS using ``snap`` as follows:

.. code-block:: bash

    sudo snap install data-science-stack

Then, you can run the DSS CLI with:

.. code-block:: bash

    dss

Initialise
----------

You can initialise DSS through ``dss initialize``.
This command:

* Stores credentials for the Canonical K8s cluster.
* Allocates storage for your DSS Jupyter Notebooks.
* Deploys an `MLflow <MLflow Docs_>`_ model registry.

.. code-block:: shell

    dss initialize --kubeconfig "$(sudo k8s config)"

The ``--kubeconfig`` option is used to provide your Canonical K8s cluster's kubeconfig.

.. note::
   Note the use of quotes for the ``--kubeconfig`` option. Without them, the content may be interpreted by your shell.

You should expect an output like this:

.. code-block:: none

    Executing initialize command
    Storing provided kubeconfig to /home/user/.dss/config
    Waiting for deployment mlflow in namespace dss to be ready...
    Deployment mlflow in namespace dss is ready
    DSS initialized. To create your first notebook run the command:

    dss create

    Examples:
      dss create my-notebook --image=pytorch
      dss create my-notebook --image=kubeflownotebookswg/jupyter-scipy:v1.8.0

Remove
------

You can remove DSS from your Canonical K8s cluster through ``dss purge``. 
This command purges all the DSS components, including:

* All Jupyter Notebooks.
* The MLflow server.
* Any data stored within the DSS environment.

.. note::

    This action removes the components of the DSS environment, but it does not remove the DSS CLI or your Canonical K8s cluster.  
    To remove those, `delete their snaps <https://snapcraft.io/docs/quickstart-tour>`_.

.. code-block:: bash

    dss purge

.. caution::

    This action is irreversible. All data stored within the DSS environment will be lost.

You should expect an output like this:

.. code-block:: none

    Waiting for namespace dss to be deleted...
    Success: All DSS components and notebooks purged successfully from the Kubernetes cluster.

Get status
----------

You can check the DSS status through ``dss status``. 
This command provides a quick way to check the status of your DSS environment, including the MLflow status and whether a GPU is detected in your environment.

.. code-block:: bash

    dss status

If you already have a DSS environment running and no GPU available, the expected output is:

.. code-block:: none

    MLflow deployment: Ready
    MLflow URL: http://10.152.183.68:5000
    GPU acceleration: Disabled

List commands
-------------

You can get the list of available commands for DSS through the ``dss`` command with the ``--help`` option:

.. code-block:: bash

    dss --help

You should expect an output like this:

.. code-block:: none

    Usage: dss [OPTIONS] COMMAND [ARGS]...

    Command line interface for managing the DSS application.

    Options:
    --help  Show this message and exit.

    Commands:
    create      Create a Jupyter notebook in DSS and connect it to MLflow.
    initialize  Initialize DSS on the given Kubernetes cluster.
    list        Lists all created notebooks in the DSS environment.
    logs        Prints the logs for the specified notebook or DSS component.
    purge       Removes all notebooks and DSS components.
    remove      Remove a Jupyter Notebook in DSS with the name NAME.
    start       Starts a stopped notebook in the DSS environment.
    status      Checks the status of key components within the DSS...
    stop        Stops a running notebook in the DSS environment.

**Get details about a specific command**:

To see the usage and options of a DSS command, run ``dss <command>`` with the ``--help`` option.
For example:

.. code-block:: bash

    dss logs --help

You should expect an output like this:

.. code-block:: none

    Usage: dss logs [OPTIONS] [NOTEBOOK_NAME]

    Prints the logs for the specified notebook or DSS component.

    Examples:
        dss logs my-notebook
        dss logs --mlflow
        dss logs --all

    Options:
    --kubeconfig TEXT  Path to a Kubernetes config file. Defaults to the value
                        of the KUBECONFIG environment variable, else to
                        './kubeconfig'.
    --all              Print the logs for all notebooks and MLflow.
    --mlflow           Print the logs for the MLflow deployment.
    --help             Show this message and exit.

See also
--------

* To learn how to manage your Jupyter Notebooks, check :ref:`manage_notebooks`. 
* If you are interested in managing MLflow within your DSS environment, see :ref:`manage_MLflow`.
