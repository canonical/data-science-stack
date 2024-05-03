Access the MLflow UI
===============================

This guide explains how to access the user interface of MLflow in the Data Science Stack (DSS) environment.

Overview
--------

Accessing the MLflow UI allows you to interact directly with your Experiments and Models. This is done through a web browser by navigating to the URL associated with MLflow.

Prerequisites
-------------

Ensure the following before attempting to access the MLflow UI:

- DSS CLI installed on your workstation.
- MLflow deployment is `Ready`.

Finding the MLflow URL
------------------------

1. **Get the MLflow URL**:

   To find the URL of MLflow, run the `dss status` command:

   .. code-block:: bash

       dss status

   Look for the `MLflow URL` in the output.

   Example output:

   .. code-block:: none

        [INFO] MLflow deployment: Ready
        [INFO] MLflow URL: http://10.152.183.205:5000

2. **Access the MLflow UI**:

   Once you have the URL from the `dss status` command, open a web browser and enter the URL into the address bar. This will direct you to the MLflow interface where you can start working with your models.


Conclusion
----------

Accessing the MLflow UI through the DSS environment is straightforward once your MLflow deployment is active and running.
