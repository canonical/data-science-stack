Create Notebook
===============

This guide provides instructions on how to create a Jupyter Notebook in the Data Science Stack (DSS) environment.

Overview
--------

A Jupyter Notebook can be created using the DSS command line interface (CLI).  This notebook will include different packages and toolkits depending on the image used to create it.

Prerequisites
-------------

Before creating a notebook, ensure you have the following:

- DSS CLI installed on your workstation
- DSS initialized

Select an Image
---------------

Before creating a notebook, you need to select an image that includes the packages and toolkits you need.
To see a list of recommended images and their aliases, see:

.. code-block:: bash

    dss create --help

The help text includes a list of recommended images and aliases so you don't need to type the full image name.
For this guide, we will use the image `kubeflownotebookswg/jupyter-scipy:v1.8.0`

Launch the Notebook
-------------------

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

Access the notebook
-------------------

To :doc:`access the Notebook </how-to/jupyter-notebook/access-ui>`, use the URL provided in the output.

Conclusion
----------

Notebooks are a powerful tool for data scientists and analysts to explore, visualise, and analyse data.  By creating a notebook in the DSS environment, you can leverage the power of the Data Science Stack to run your analyses.

Next Steps
^^^^^^^^^^

* Want to leverage your NVIDIA GPU? Try :ref:`nvidia-gpu`
* Want to learn how to interact with your Notebooks? Try :ref:`jupyter-notebooks`
* Want to learn more about handling data? See :ref:`access-data`
* Want to connect to MLflow? See :ref:`notebook-mlflow`
