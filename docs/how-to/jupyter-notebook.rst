.. _manage_notebooks:

Manage Jupyter Notebooks
========================

This guide describes how to manage Jupyter Notebooks within your Data Science Stack (DSS) environment.

Create Notebook
---------------

This guide provides instructions on how to create a Jupyter Notebook in the Data Science Stack (DSS) environment.

A Jupyter Notebook can be created using the DSS command line interface (CLI).  
This notebook will include different packages and toolkits depending on the image used to create it.

Prerequisites
~~~~~~~~~~~~~

Before creating a notebook, ensure you have the following:

- DSS CLI installed on your workstation
- DSS initialized

Creating a Notebook
~~~~~~~~~~~~~~~~~~~

1. **Select an image**:

    Before creating a notebook, you need to select an image that includes the packages and toolkits you need.  To see a list of recommended images and their aliases, see:

    .. code-block:: bash

        dss create --help

    The help text includes a list of recommended images and aliases so you don't need to type the full image name.  For this guide, we will use the image `kubeflownotebookswg/jupyter-scipy:v1.8.0`

2. **Create the notebook**:

    Create a new notebook using ``dss create``:

    .. code-block:: bash

        dss create my-notebook --image kubeflownotebookswg/jupyter-scipy:v1.8.0

    This will pull the notebook image and start a Notebook server, printing the URL of the notebook once complete.  Expected output:

    .. code-block:: none

        [INFO] Executing create command
        [INFO] Waiting for deployment test-notebook in namespace dss to be ready...
        [INFO] Deployment test-notebook in namespace dss is ready
        [INFO] Success: Notebook test-notebook created successfully.
        [INFO] Access the notebook at http://10.152.183.42:80.

3. **Access the notebook**:

    To :doc:`access the Notebook </how-to/jupyter-notebook/access-ui>`, use the URL provided in the output.

List Created Notebooks
----------------------

This guide explains how to use the `dss list` command to view the current status of all notebooks within the Data Science Stack (DSS) environment.

The `dss list` command provides a snapshot of all notebooks along with their current states. Understanding these states helps you manage and interact with your notebooks effectively.

Using the `dss list` Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To view the list and status of all notebooks, run the following command in your DSS environment:

.. code-block:: bash

    dss list

This command displays each notebook along with its current state and URL if applicable. Here is an example of what you might see:

.. code-block:: none

    Name          Image                                               URL                      
    my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80  (Active)
    data-prep     kubeflownotebookswg/jupyter-minimal:v1.5.0          (Downloading)
    test-env      kubeflownotebookswg/jupyter-scipy-notebook:v1.9.0   (Stopping)

Notebook States
~~~~~~~~~~~~~~~

Each notebook can be in one of the following states:

- **Active**: The notebook is running and accessible. The URL under the "URL" column will be displayed, allowing you to access the notebook directly.

- **Stopped**: The notebook is not running. You can start it using the `dss start` command.

- **Stopping**: The notebook is in the process of stopping. It is advisable to wait until the process completes, transitioning to "Stopped".

- **Starting**: The notebook is starting up. This state indicates that the notebook is initialising and will soon be active.

- **Downloading**: The notebook is downloading the specified OCI Image.. This is usually a transient state before it becomes "Active".

- **Removing**: The command to remove the notebook has been issued (`dss remove`), but the notebook has not been completely removed yet. This state will eventually clear once the notebook is fully removed.

Delete a Notebook
-----------------

This guide provides instructions on how to remove a Jupyter Notebook from the Data Science Stack (DSS) environment.

Deleting a Jupyter Notebook is useful when you no longer need the notebook and want to clear up resources or declutter your workspace. This process is handled through the DSS command line interface (CLI), and it is non-blocking, meaning you can continue other work while the deletion completes.

.. note::

   When you delete a notebook, any data stored under `~/shared` within the notebook will be preserved and remain accessible to other notebooks. This shared storage is designed to ensure that valuable data is not lost even when individual notebooks are removed from the environment.

Prerequisites
~~~~~~~~~~~~~

Before deleting a notebook, ensure you have the following:

- DSS CLI installed on your workstation.
- The notebook you wish to delete.

Deleting a Notebook
~~~~~~~~~~~~~~~~~~~

1. **Check the existing notebooks**:

   Before deletion, verify the notebook you want to delete is listed and check its status with the `dss list` command:

   .. code-block:: bash

       dss list

   Example output:

   .. code-block:: none

       Name          Image                                               URL                       
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

2. **Remove the notebook**:

   To delete the notebook, use the `dss remove` command followed by the name of the notebook:

   .. code-block:: bash

       dss remove my-notebook

   Expected output:

   .. code-block:: none

       Removing the notebook my-notebook. Check `dss list` for the status of the notebook.

3. **Verify the notebook has been removed**:

   After initiating the remove command, the notebook may go through a "Removing" state. To confirm the notebook has been removed, run the `dss list` command again:

   .. code-block:: bash

       dss list

   If the notebook has been successfully removed, it will no longer appear in the list. If it's still showing as "Removing", you may need to wait a bit longer or investigate if there are any issues preventing the deletion.

Start a Notebook
----------------

This guide provides instructions on how to start a stopped Jupyter Notebook within the Data Science Stack (DSS) environment.

A Jupyter Notebook that has been stopped can be restarted using the DSS command line interface (CLI). This allows you to resume your work without needing to configure a new notebook.

Prerequisites
~~~~~~~~~~~~~

Before starting a notebook, ensure you have the following:

- DSS CLI installed on your workstation.
- A stopped notebook. You can verify the status of notebooks using the ``dss list`` command.

Starting a Stopped Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **List the available notebooks**:

   First, use the ``dss list`` command to display all notebooks and their statuses:

   .. code-block:: bash

       dss list

   Example output:

   .. code-block:: none

       Name          Image                                               URL       
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  (Stopped)

   This shows that ``my-notebook`` is currently stopped.

2. **Start the notebook**:

   To start the notebook, use the ``dss start`` command followed by the name of the notebook:

   .. code-block:: bash

       dss start my-notebook

   Expected output:

   .. code-block:: none

       Executing start command
       Starting the notebook my-notebook. Check `dss list` for the status of the notebook.

3. **Verify the notebook is running**:

   After initiating the start command, the notebook may go through statuses such as *Starting* or *Downloading*. To check the current status and access the URL once ready, run:

   .. code-block:: bash

       dss list

   Example output when the notebook is ready:

   .. code-block:: none

       Name          Image                                               URL                      
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

   This URL can be used to access your Jupyter Notebook.

Stop a Notebook
---------------

This guide provides instructions on how to stop a running Jupyter Notebook within the Data Science Stack (DSS) environment.

Stopping a Jupyter Notebook that is in use helps free up resources and ensures data safety when not actively working on the notebook. This guide covers the process of stopping a notebook using the DSS command line interface (CLI).

Prerequisites
~~~~~~~~~~~~~

Before stopping a notebook, ensure you have the following:

- DSS CLI installed on your workstation.
- A running notebook. You can verify the status of notebooks using the ``dss list`` command.

Stopping a Running Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **List the available notebooks**:

   Use the ``dss list`` command to display all notebooks and their current statuses:

   .. code-block:: bash

       dss list

   Example output might show a running notebook:

   .. code-block:: none

       Name          Image                                               URL                      
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80 

2. **Stop the notebook**:

   To stop a running notebook, use the ``dss stop`` command followed by the name of the notebook:

   .. code-block:: bash

       dss stop my-notebook

   Expected output:

   .. code-block:: none

       Stopping the notebook my-notebook. Check `dss list` for the status of the notebook.

3. **Verify the notebook has stopped**:

   After initiating the stop command, the notebook will go through a "Stopping" state. To confirm the notebook has stopped, run the `dss list` command again:

   .. code-block:: bash

       dss list

   Example output when the notebook is stopped:

   .. code-block:: none

       Name          Image                                               URL       
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  (Stopped)

.. _access-ui:

Access the Jupyter Notebooks UI
-------------------------------

This guide explains how to access the user interface of a Jupyter Notebook running in the Data Science Stack (DSS) environment.

Accessing the Jupyter Notebook UI allows you to interact directly with your notebooks, run code, and visualise data. This is done through a web browser by navigating to the URL associated with your active notebook.

Prerequisites
~~~~~~~~~~~~~

Ensure the following before attempting to access the Notebook UI:

- DSS CLI installed on your workstation.
- At least one notebook is currently active in the DSS environment.

Finding the Notebook URL
~~~~~~~~~~~~~~~~~~~~~~~~

1. **List active notebooks**:

   To find the URL of your Jupyter Notebook, first ensure that it is active. Run the `dss list` command to see all the notebooks and their statuses:

   .. code-block:: bash

       dss list

   Look for the notebook in the output, and specifically check the URL column. An active notebook will have a URL listed, which indicates it is ready for access.

   Example output:

   .. code-block:: none

       Name          Image                                               URL                      
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

2. **Access the Notebook UI**:

   Once you have the URL from the `dss list` command, open a web browser and enter the URL into the address bar. This will direct you to the Jupyter Notebook interface where you can start working with your notebook.

   Ensure that the notebook is in an active state. If the notebook is not active, you may need to start it or check for any issues that are preventing it from being accessible.

Get Notebook Logs
-----------------

This guide provides instructions on how to retrieve logs for a Jupyter Notebook running in the Data Science Stack (DSS) environment.

Retrieving logs for a Jupyter Notebook can help you troubleshoot issues, monitor notebook activities, or verify actions taken in the notebook. This process uses the DSS command line interface (CLI).

Prerequisites
~~~~~~~~~~~~~

Before accessing the logs, ensure you have the following:

- DSS CLI installed on your workstation.
- A notebook whose logs you wish to view.

Retrieving Notebook Logs
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Identify the notebook**:

   Determine the name of the notebook you want to retrieve logs for. You can list all available notebooks and their statuses using the `dss list` command if needed:

   .. code-block:: bash

       dss list

2. **Retrieve the logs**:

   To get the logs for the notebook, use the `dss logs` command followed by the name of the notebook:

   .. code-block:: bash

       dss logs my-notebook

   Expected output:

   .. code-block:: none

        [INFO] Logs for my-notebook2-8cf4d9bc-jm9zm:
        [INFO] s6-rc: info: service s6rc-oneshot-runner: starting
        [INFO] s6-rc: info: service s6rc-oneshot-runner successfully started
        [INFO] s6-rc: info: service fix-attrs: starting
        [INFO] s6-rc: info: service fix-attrs successfully started
        [INFO] s6-rc: info: service legacy-cont-init: starting
        [INFO] cont-init: info: running /etc/cont-init.d/01-copy-tmp-home
        [INFO] cont-init: info: /etc/cont-init.d/01-copy-tmp-home exited 0
        [INFO] s6-rc: info: service legacy-cont-init successfully started
        [INFO] s6-rc: info: service legacy-services: starting
        [INFO] services-up: info: copying legacy longrun jupyterlab (no readiness notification)
        [INFO] s6-rc: info: service legacy-services successfully started
        [INFO] [W 2024-04-30 13:44:20.991 ServerApp] ServerApp.token config is deprecated in 2.0. Use IdentityProvider.token.
        [INFO] [I 2024-04-30 13:44:20.996 ServerApp] Package jupyterlab took 0.0000s to import
        [INFO] [I 2024-04-30 13:44:20.997 ServerApp] Package jupyter_server_fileid took 0.0013s to import
        [INFO] [I 2024-04-30 13:44:20.998 ServerApp] Package jupyter_server_mathjax took 0.0007s to import
        [INFO] [I 2024-04-30 13:44:21.001 ServerApp] Package jupyter_server_terminals took 0.0024s to import
        [INFO] [I 2024-04-30 13:44:21.012 ServerApp] Package jupyter_server_ydoc took 0.0105s to import
        [INFO] [I 2024-04-30 13:44:21.022 ServerApp] Package jupyterlab_git took 0.0104s to import
        [INFO] [I 2024-04-30 13:44:21.022 ServerApp] Package nbclassic took 0.0000s to import

.. _notebook-mlflow:

Connect from Notebook to MLflow
-------------------------------

This guide provides instructions on how to integrate MLflow with your Jupyter Notebook in the Data Science Stack (DSS) environment for tracking experiments.

MLflow is a platform for managing the end-to-end machine learning life cycle. It includes tracking experiments, packaging code into reproducible runs, and sharing and deploying models. DSS environments are pre-configured to interact with an MLflow server through the `MLFLOW_TRACKING_URI` environment variable set in each notebook.

Prerequisites
~~~~~~~~~~~~~

Before you begin, ensure the following:

- You have an active Jupyter Notebook in the DSS environment.
- You understand basic operations within a Jupyter Notebook.

Installing MLflow
~~~~~~~~~~~~~~~~~

To interact with MLflow, the MLflow Python library needs to be installed within your notebook environment. There are two ways to install the MLflow library:

1. **Within a Notebook Cell** (Recommended):

   It's recommended to install MLflow directly within a notebook cell to ensure the library is available for all subsequent cells during your session.

   .. code-block:: none

       %%bash
       pip install mlflow

2. **Using the Notebook's Terminal**:

   Alternatively, you can install MLflow from the notebook's terminal with the same command. This method also installs MLflow for the current session:

   .. code-block:: bash

       pip install mlflow

   Remember, any installations via the notebook or terminal will not persist after the notebook is restarted (e.g., stopped and started again with `dss start` and `dss stop`). Therefore, the first method is preferred to ensure consistency across sessions.

Connecting to MLflow library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing MLflow, you can directly interact with the MLflow server configured for your DSS environment:

.. code-block:: python

    import mlflow

    # Initialise the MLflow client
    c = mlflow.MlflowClient()

    # The tracking URI should be set automatically from the environment variable
    print(c.tracking_uri)  # Prints the MLflow tracking URI

    # Create a new experiment
    c.create_experiment("test-experiment")

This example shows how to initialise the MLflow client, check the tracking URI, and create a new experiment. The `MLFLOW_TRACKING_URI` should already be set in your environment, allowing you to focus on your experiments without manual configuration.

For more detailed information on using MLflow, including advanced configurations and features, refer to the official MLflow documentation:

* `MLflow Docs`_

.. _access-data:

Access your data from DSS
-------------------------

This guide provides instructions on how to access the stored data from your Notebooks in the Data Science Stack (DSS) environment.

Accessing your data is useful when you want to browse or modify the files stored from your Notebooks.

Prerequisites
~~~~~~~~~~~~~
Before accessing your data, ensure you have the following:

- DSS CLI installed on your workstation.
- At least one notebook was created in the DSS environment.

Accessing your data
~~~~~~~~~~~~~~~~~~~
By default, your Notebooks data will be stored in a directory under `/var/snap/microk8s/common/default-storage`:

* `Microk8s hostpath docs`_

This directory is shared by all DSS Notebooks.

1. **Find the directory of your stored data**
    To find the directory containing your Notebooks data, list the directories under `/var/snap/microk8s/common/default-storage`:

    .. code-block:: bash

        ls /var/snap/microk8s/common/default-storage/


    Expected output:

    .. code-block:: bash

        dss-notebooks-pvc-00037e23-e2e2-4ab4-9088-45099154da30

    The storage directory is the one prefixed with `dss-notebooks-pvc` as shown in the output.

    .. note::

        The characters that follow the `dss-notebooks-pvc-` will not be the same for all DSS environments.

2. **Access your Notebooks data**
    From your local file browser, navigate to the folder `/var/snap/microk8s/common/default-storage/[directory name]`. Use the directory name you got from the previous step.

    Now, you can view and manage all your stored Notebooks data.



