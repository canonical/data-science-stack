Connect from Notebook to MLflow
===============================

This guide provides instructions on how to integrate MLflow with your Jupyter Notebook in the Data Science Stack (DSS) environment for tracking experiments.

Overview
--------

MLflow is a platform for managing the end-to-end machine learning life cycle. It includes tracking experiments, packaging code into reproducible runs, and sharing and deploying models. DSS environments are pre-configured to interact with an MLflow server through the `MLFLOW_TRACKING_URI` environment variable set in each notebook.

Prerequisites
-------------

Before you begin, ensure the following:

- You have an active Jupyter Notebook in the DSS environment.
- You understand basic operations within a Jupyter Notebook.

Installing MLflow
-----------------

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
----------------------------

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

Further Information
-------------------

For more detailed information on using MLflow, including advanced configurations and features, refer to the official MLflow documentation:

* `MLflow Docs`_

Conclusion
----------

By following these steps, you can seamlessly integrate MLflow into your Jupyter Notebooks within the DSS environment, leveraging robust tools for managing your machine learning experiments effectively.

