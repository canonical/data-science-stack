.. _manage_notebooks:

Manage Jupyter Notebooks
========================

This guide describes how to manage `Jupyter Notebooks`_ within your Data Science Stack (DSS) environment.

All actions can be performed using the DSS Command Line Interface (CLI). 

Create a notebook
-----------------

You can create a Jupyter Notebook using the DSS CLI.
This notebook includes different packages and toolkits depending on the image used to create it.

1. **Select an image**:

Before creating a notebook, you need to select an image that includes the packages and toolkits you need.  
To see a list of recommended images and their aliases, do:

.. code-block:: bash

    dss create --help

The output includes a list of recommended images and their aliases.
For example, this guide uses the image `kubeflownotebookswg/jupyter-scipy:v1.8.0`

2. **Create the notebook**:

Create a new notebook as follows:

.. code-block:: bash

    dss create my-notebook --image kubeflownotebookswg/jupyter-scipy:v1.8.0

This command starts a notebook server with the selected image.
You should expect an output like this: 

.. code-block:: none

    [INFO] Executing create command
    [INFO] Waiting for deployment test-notebook in namespace dss to be ready...
    [INFO] Deployment test-notebook in namespace dss is ready
    [INFO] Success: Notebook test-notebook created successfully.
    [INFO] Access the notebook at http://10.152.183.42:80.

Create an NVIDIA GPU-enabled notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create an NVIDIA GPU-enabled Jupyter Notebook containing CUDA runtimes and ML frameworks, and access its JupyterLab server.

.. note::

   To launch an NVIDIA GPU-enabled notebook, you must first :ref:`install <install_nvidia_operator>`
   the NVIDIA Operator and :ref:`verify <verify_nvidia_operator>` DSS can detect the GPU.
   See :ref:`nvidia_gpu` for more details.

To see the list of available CUDA images, run:

.. code-block:: bash

   dss create --help | grep cuda

You should see an output similar to this:

.. code-block:: bash

        - pytorch-cuda = kubeflownotebookswg/jupyter-pytorch-cuda-full:v1.8.0
        - tensorflow-cuda = kubeflownotebookswg/jupyter-tensorflow-cuda-full:v1.8.0

Select one of them and create a notebook as follows:

.. code-block:: bash

   dss create my-notebook --image=tensorflow-cuda


Confirm the GPU is detected and usable by running:

.. code-block:: python

   import tensorflow as tf

   tf.config.list_physical_devices('GPU')

Create an Intel GPU-enabled notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create an Intel GPU-enabled Jupyter Notebook with `Intel Extension for PyTorch (IPEX) <https://github.com/intel/intel-extension-for-pytorch?tab=readme-ov-file#intel-extension-for-pytorch>`_ 
or `Intel Extension for TensorFlow (ITEX) <https://github.com/intel/intel-extension-for-tensorflow?tab=readme-ov-file#intel-extension-for-tensorflow>`_.

.. note::

   To launch an Intel GPU-enabled notebook, you must first :ref:`enable_intel_gpu`.

To see the list of available Intel images, run:

.. code-block:: bash

   dss create --help | grep intel

You should see an output similar to this:

.. code-block:: bash

        - intel-pytorch = intel/intel-extension-for-pytorch:2.1.20-xpu-idp-jupyter
        - intel-tensorflow = intel/intel-extension-for-tensorflow:2.15.0-xpu-idp-jupyter

Select one of them and create a notebook as follows:

.. code-block:: bash

   dss create my-itex-notebook --image=intel-tensorflow

Confirm the GPU is detected and usable by running:

.. code-block:: python

   import tensorflow as tf

   tf.config.experimental.list_physical_devices()

For example, you should expect an output like the following for a host system containing an Intel CPU and a single Intel GPU:

.. code-block:: python

    [PhysicalDevice(name='/physical_device:CPU:0', device_type='CPU'), PhysicalDevice(name='/physical_device:XPU:0', device_type='XPU')]

.. note::

    Intel denotes XPU the combination of an Intel CPU with GPU.

List created notebooks
----------------------

You can check the current state of all notebooks within your DSS environment.
To view the full list, run:

.. code-block:: bash

    dss list

This command displays each notebook name along with its associated image, state and URL if applicable. 
For example:

.. code-block:: none

    Name          Image                                               URL                      
    my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80  (Active)
    data-prep     kubeflownotebookswg/jupyter-minimal:v1.5.0          (Downloading)
    test-env      kubeflownotebookswg/jupyter-scipy-notebook:v1.9.0   (Stopping)

.. _notebook_states:

Notebook states
~~~~~~~~~~~~~~~

Each notebook can be in one of the following states:

* **Active**: The notebook is running and accessible. You can use the URL under the *URL* column to access it.

* **Stopped**: The notebook is not running. 

* **Stopping**: The notebook is in the process of stopping. It is advisable to wait until the process completes, transitioning to *Stopped*.

* **Starting**: The notebook is initialising and will soon be *Active*.

* **Downloading**: The notebook is downloading the specified OCI Image. This is a transient state before it becomes *Active*.

* **Removing**: The notebook is in the process of being removed. This is a transient state before it is fully removed.

Remove a notebook
-----------------

You can remove a Jupyter Notebook using the DSS CLI.
It is a non-blocking process, meaning you can continue other work while the deletion completes.

.. note::

   When you remove a notebook, any data stored under `~/shared` within the notebook will be preserved and remain accessible to other notebooks. 
   This shared storage is designed to ensure that valuable data is not lost even when individual notebooks are removed from the environment.

1. **Remove the notebook**:

To delete the notebook, use the ``dss remove`` command followed by the name of the notebook, ``my-notebook`` in this example:

.. code-block:: bash

    dss remove my-notebook

You should expect an output like this:

.. code-block:: none

    Removing the notebook my-notebook. Check `dss list` for the status of the notebook.

2. **Verify the notebook has been removed**:

To confirm the notebook has been removed, you can check the list of notebooks again: 

.. code-block:: bash

    dss list

If the notebook has been successfully removed, it will no longer appear in the list. 
If it's still showing as *Removing*, you may need to wait a bit longer or investigate if there are any issues preventing its deletion.

.. _start_notebook:

Start a notebook
----------------

You can start a notebook using the DSS CLI.
This enables you to resume your work without needing to configure a new notebook.

1. **Start the notebook**:

To start the notebook, use the ``dss start`` command followed by the name of the notebook, ``my-notebook`` in this example:

.. code-block:: bash

    dss start my-notebook

You should expect an output like this:

.. code-block:: none

    Executing start command
    Starting the notebook my-notebook. Check `dss list` for the status of the notebook.

2. **Verify the notebook is running**:

After starting it, the notebook may go through :ref:`different states <notebook_states>`. 
To check its state, run:

.. code-block:: bash

    dss list

Once ready, you should expect an output like this:

.. code-block:: none

    Name          Image                                               URL                      
    my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

You can use this URL to :ref:`access the notebook <access_notebook>`.

Stop a notebook
---------------

You can stop a notebook using the DSS CLI.
Stopping a notebook frees up resources and ensures data safety when not actively working on it. 

1. **Stop the notebook**:

To stop a running notebook, use the ``dss stop`` command followed by the name of the notebook, ``my-notebook`` in this example:

.. code-block:: bash

    dss stop my-notebook

You should see an output like this:

.. code-block:: none

    Stopping the notebook my-notebook. Check `dss list` for the status of the notebook.

2. **Verify the notebook has stopped**:

After stopping it, the notebook may go through :ref:`different states <notebook_states>`. 
To confirm it has stopped, check its state:

.. code-block:: bash

    dss list

You should expect an output like this: 

.. code-block:: none

    Name          Image                                               URL       
    my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  (Stopped)

.. _access_notebook:

Access a notebook
-----------------

You can access a notebook User Interface (UI) using the DSS CLI.
Accessing the UI enables you to interact directly with your notebook, run code, and visualise data. 
This is done through a web browser by navigating to the URL associated with your active notebook.

.. note::

    Ensure your notebook is in *Active* :ref:`state <notebook_states>` to be able to access it.
    Otherwise, you may need to :ref:`start <start_notebook>` it or check for any issues that are preventing it from being accessible.

1. **Find the notebook URL**:

To find the URL of your notebook, first list all the notebooks:

.. code-block:: bash

    dss list

Look for your notebook in the output, and specifically check the URL column. 
An active notebook has associated a URL, which indicates it is ready for accessing.

You should expect an output like this:

.. code-block:: none

    Name          Image                                               URL                      
    my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

2. **Access the Notebook UI**:

Once you know the URL, open a web browser and enter the URL into the address bar. 
This will direct you to the notebook UI where you can start working with your notebook.   

Get notebook logs
-----------------

You can retrieve logs for a Jupyter Notebook using the DSS CLI.
Retrieving logs can help you troubleshoot issues, monitor notebook activities, or verify actions taken in the notebook. 

To get the logs for a certain notebook, use the ``dss logs`` command followed by the name of the notebook, ``my-notebook`` in this example:

.. code-block:: bash
    
    dss logs my-notebook

You should expect an output like this:

.. code-block:: none

    [INFO] Logs for my-notebook-8cf4d9bc-jm9zm:
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

Connect from notebook to MLflow
-------------------------------

You can integrate `MLflow <Charmed MLflow_>`_ with your Jupyter Notebook for tracking experiments using DSS. 

MLflow is a platform for managing the end-to-end machine learning life cycle. 
It includes tracking experiments, packaging code into reproducible runs, and sharing and deploying models. 

DSS environments are pre-configured to interact with an MLflow server through the `MLFLOW_TRACKING_URI` environment variable set in each notebook.

Installing MLflow
~~~~~~~~~~~~~~~~~

To interact with MLflow, the MLflow Python library needs to be installed within your notebook environment. 
There are two ways to install the MLflow library:

1. **Within a notebook cell** (Recommended):

It's recommended to install MLflow directly within a notebook cell to ensure the library is available for all subsequent cells during your session:

.. code-block:: none

    %%bash
    pip install mlflow

2. **Using the notebook terminal**:

Alternatively, you can install MLflow from the notebook terminal with the same command. 
This method also installs MLflow for the current session:

.. code-block:: bash

    pip install mlflow

Note that any installations via the notebook or terminal will not persist after the notebook is restarted.
Therefore, the first method is preferred to ensure consistency across sessions.

Connecting to MLflow library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing MLflow, you can directly interact with the MLflow server configured for your DSS environment:

.. code-block:: python

    import mlflow

    c = mlflow.MlflowClient()

    print(c.tracking_uri)  

    c.create_experiment("test-experiment")

This example shows how to initialise the MLflow client, check the tracking URI, and create a new experiment. 
The `MLFLOW_TRACKING_URI` should already be set in your environment, allowing you to focus on your experiments without manual configuration.

For more detailed information on using MLflow, including advanced configurations and features, refer to the official `MLflow Docs`_.

.. _access-data:

Access your data from DSS
-------------------------

You can access the stored data from your notebooks using the DSS CLI.
Accessing your data is useful when you want to browse or modify the files stored from your notebooks.

.. note::
    By default, your notebooks data are stored in a directory under `/var/snap/microk8s/common/default-storage`. 
    See `Microk8s hostpath docs`_ for more information.

This directory is shared by all your DSS notebooks.

1. **Find the directory of your stored data**
    
To find the directory containing your notebooks data, list the directories under `/var/snap/microk8s/common/default-storage`:

.. code-block:: bash

    ls /var/snap/microk8s/common/default-storage/


You should see an output like this:

.. code-block:: bash

    dss-notebooks-pvc-00037e23-e2e2-4ab4-9088-45099154da30

The storage directory is the one prefixed with `dss-notebooks-pvc` as shown in the output.

.. note::

    The characters that follow `dss-notebooks-pvc-` may not be the same for all DSS environments.

2. **Access your notebooks data**

From your local file browser, navigate to the folder `/var/snap/microk8s/common/default-storage/[directory name]`. 
Use the directory name you got from the previous step.

Now, you can view and manage all your stored notebooks data.

See also
--------

* To learn how to manage your DSS environment, check :ref:`manage_DSS`. 
* If you are interested in managing MLflow within your DSS environment, see :ref:`manage_MLflow`.

