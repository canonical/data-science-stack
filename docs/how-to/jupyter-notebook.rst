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

    Executing create command
    Waiting for deployment test-notebook in namespace dss to be ready...
    Deployment test-notebook in namespace dss is ready
    Success: Notebook test-notebook created successfully.
    Access the notebook at http://10.152.183.42:80.

Create an NVIDIA GPU-enabled notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create an NVIDIA GPU-enabled Jupyter Notebook containing CUDA runtimes and Machine Learning (ML) frameworks, and access its JupyterLab server.

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

You can confirm your GPU is detected and usable by running the following within your notebook:

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

        - pytorch-intel= intel/intel-extension-for-pytorch:2.1.20-xpu-idp-jupyter
        - tensorflow-intel = intel/intel-extension-for-tensorflow:2.15.0-xpu-idp-jupyter

Select one of them and create a notebook as follows:

.. code-block:: bash

   dss create my-itex-notebook --image=tensorflow-intel

You can confirm your Intel GPU is detected and usable by running the following within your notebook:

.. code-block:: python

   import tensorflow as tf

   tf.config.experimental.list_physical_devices()

List created notebooks
----------------------

You can check the current state of all notebooks within your DSS environment.
To view the full list, run:

.. code-block:: bash

    dss list

This command displays each notebook name along with its associated image, state, and URL if applicable. 

Remove a notebook
-----------------

You can remove a Jupyter Notebook using the DSS CLI.
It is a non-blocking process, meaning you can continue other work while the deletion completes.

1. **Remove the notebook**:

To delete the notebook, use the ``dss remove`` command followed by the name of the notebook, ``my-notebook`` in this example:

.. code-block:: bash

    dss remove my-notebook

You should expect an output like this:

.. code-block:: none

    Removing the notebook my-notebook. Check `dss list` for the status of the notebook.

Start a notebook
----------------

You can start a notebook using the DSS CLI.
This enables you to resume your work without needing to configure a new notebook.

.. code-block:: bash

    dss start my-notebook

Stop a notebook
---------------

You can stop a notebook using the DSS CLI.
Stopping a notebook frees up resources and ensures data safety when not actively working on it. 

.. code-block:: bash

    dss stop my-notebook

Access a notebook
-----------------

You can access a notebook User Interface (UI) using the DSS CLI.
Accessing the UI enables you to interact directly with your notebook, run code, and visualise data. 
This is done through a web browser by navigating to the URL associated with your active notebook.

1. **Find the notebook URL**:

To find the URL of your notebook, first list all the notebooks:

.. code-block:: bash

    dss list

Look for your notebook in the output, and specifically check the URL column. 

2. **Access the Notebook UI**:

Once you know the URL, open a web browser and enter the URL into the address bar. 

Get notebook logs
-----------------

You can retrieve logs for a Jupyter Notebook using the DSS CLI.
Retrieving logs can help you troubleshoot issues, monitor notebook activities, or verify actions taken in the notebook. 

.. code-block:: bash
    
    dss logs my-notebook

See also
--------

* To learn how to manage your DSS environment, check :ref:`manage_DSS`. 
* If you are interested in managing MLflow within your DSS environment, see :ref:`manage_MLflow`.

