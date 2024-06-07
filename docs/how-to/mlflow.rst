Manage MLflow
=============

This guide describes how to manage MLflow within the Data Science Stack (DSS).

Access the MLflow UI
--------------------

This guide explains how to access the MLflow User Interface (UI) within the Data Science Stack (DSS) environment.

Accessing the MLflow UI allows you to interact directly with your Experiments and Models. This is done through a web browser by navigating to the URL associated with MLflow.

Prerequisites
~~~~~~~~~~~~~

Ensure the following before attempting to access the MLflow UI:

- DSS CLI installed on your workstation.
- MLflow deployment is `Ready`.

Finding the MLflow URL
~~~~~~~~~~~~~~~~~~~~~~

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

Get MLflow logs
---------------

This guide provides instructions on how to retrieve logs for MLflow in the Data Science Stack (DSS) environment.
Retrieving logs is a critical task for maintaining and troubleshooting MLflow in the DSS environment. 
This guide has shown you how to access logs quickly to help ensure your MLflow deployment is running smoothly and efficiently.

Retrieving logs for MLflow can help you troubleshoot issues. This process uses the DSS command line interface (CLI).

Prerequisites
~~~~~~~~~~~~~

Before accessing the logs, ensure you have the following:

- DSS CLI installed on your workstation.
- MLflow deployment is `Ready`.

Retrieving MLflow logs
~~~~~~~~~~~~~~~~~~~~~~

**Retrieve the logs**:

   To get the logs for MLflow, use the `dss logs` command followed by the `--mlflow` option:

   .. code-block:: bash

       dss logs --mlflow

   Expected output:

   .. code-block:: none
    
        [INFO] Logs for mlflow-6bbfc5db5-xlfvj:
        [INFO] [2024-04-30 07:57:54 +0000] [22] [INFO] Starting gunicorn 20.1.0
        [INFO] [2024-04-30 07:57:54 +0000] [22] [INFO] Listening at: http://0.0.0.0:5000 (22)
        [INFO] [2024-04-30 07:57:54 +0000] [22] [INFO] Using worker: sync
        [INFO] [2024-04-30 07:57:54 +0000] [23] [INFO] Booting worker with pid: 23
        [INFO] [2024-04-30 07:57:54 +0000] [24] [INFO] Booting worker with pid: 24
        [INFO] [2024-04-30 07:57:54 +0000] [25] [INFO] Booting worker with pid: 25
        [INFO] [2024-04-30 07:57:54 +0000] [26] [INFO] Booting worker with pid: 26



