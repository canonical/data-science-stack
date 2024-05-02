Get MLFlow Logs
=================

This guide provides instructions on how to retrieve logs for MLFlow in the Data Science Stack (DSS) environment.

Overview
--------

Retrieving logs for MLFlow can help you troubleshoot issues. This process uses the DSS command line interface (CLI).

Prerequisites
-------------

Before accessing the logs, ensure you have the following:

- DSS CLI installed on your workstation.
- MLFlow deployment is `Ready`.

Retrieving MLFlow Logs
------------------------

**Retrieve the logs**:

   To get the logs for MLFlow, use the `dss logs` command followed by the `--mlflow` option:

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


Conclusion
----------

Retrieving logs is a critical task for maintaining and troubleshooting MLFlow in the DSS environment. This guide has shown you how to access logs quickly to help ensure your MLFlow deployment is running smoothly and efficiently.

