List DSS commands
===========================

This guide provides instructions on how to list the available commands to interact with the Data Science Stack (DSS) environment.

Overview
--------

Interacting with the Data Science Stack (DSS) is done through the command line interface (CLI). 

Prerequisites
-------------
Before listing the available commands, you need to make sure that DSS CLI installed on your workstation.

Listing available DSS commands
------------------------------

**List the commands**:

    To get the list of available commands for DSS, run `dss` with the `--help` option:

    .. code-block:: bash

        dss --help

    Expected output:

    .. code-block:: none

        Usage: dss [OPTIONS] COMMAND [ARGS]...

        Command line interface for managing the DSS application.

        Options:
        --help  Show this message and exit.

        Commands:
        create      Create a Jupyter notebook in DSS and connect it to MLFlow.
        initialize  Initialize DSS on the given Kubernetes cluster.
        list        Lists all created notebooks in the DSS environment.
        logs        Prints the logs for the specified notebook or DSS component.
        purge       Removes all notebooks and DSS components.
        remove      Remove a Jupter Notebook in DSS with the name NAME.
        start       Starts a stopped notebook in the DSS environment.
        status      Checks the status of key components within the DSS...
        stop        Stops a running notebook in the DSS environment.

    
**Get details about a specific command**:

    To see the usage and options of a DSS command, run `dss <command>`` with the `--help` option:

    For Example:

    .. code-block:: bash

        dss logs --help

    Expected output:

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
