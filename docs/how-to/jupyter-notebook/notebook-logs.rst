Get Notebook Logs
=================

This guide provides instructions on how to retrieve logs for a Jupyter Notebook running in the Data Science Stack (DSS) environment.

Overview
--------

Retrieving logs for a Jupyter Notebook can help you troubleshoot issues, monitor notebook activities, or verify actions taken in the notebook. This process uses the DSS command line interface (CLI).

Prerequisites
-------------

Before accessing the logs, ensure you have the following:

- DSS CLI installed on your workstation.
- A notebook whose logs you wish to view.

Retrieving Notebook Logs
------------------------

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

       [INFO] Logs for my-notebook-6d47c6f9f7-5bjqd:
       [INFO] 2024-04-30T10:09:11.497Z [pebble] Started daemon.
       [INFO] 2024-04-30T10:09:11.528Z [pebble] POST /v1/services 15.363608ms 202
       [INFO] 2024-04-30T10:09:11.528Z [pebble] Started default services with change 1.
       [INFO] 2024-04-30T10:09:11.543Z [pebble] Service "jupyter" starting: ./jupyter lab --notebook-dir="/home/jovyan" --ip=0.0.0.0 --no-browser --port=8888 --ServerApp.token="" --ServerApp.password="" --ServerApp.allow_origin="*" --ServerApp.base_url="/" --ServerApp.authenticate_prometheus="False"
       [INFO] 2024-04-30T10:09:12.932Z [jupyter] [W 2024-04-30 10:09:12.932 ServerApp] ServerApp.token config is deprecated in 2.0. Use IdentityProvider.token.
       [INFO] 2024-04-30T10:09:13.034Z [jupyter] [W 2024-04-30 10:09:13.033 ServerApp] A `_jupyter_server_extension_points` function was not found in nbclassic. Instead, a `_jupyter_server_extension_paths` function was found and will be used for now. This function name will be deprecated in future releases of Jupyter Server.
       [INFO] 2024-04-30T10:09:13.036Z [jupyter] [I 2024-04-30 10:09:13.036 ServerApp] jupyter_server_fileid | extension was successfully linked.
       [INFO] 2024-04-30T10:09:13.038Z [jupyter] [I 2024-04-30 10:09:13.038 ServerApp] jupyter_server_mathjax | extension was successfully linked.
Conclusion
----------

Retrieving logs is a critical task for maintaining and troubleshooting Jupyter Notebooks in the DSS environment. This guide has shown you how to access logs quickly to help ensure your notebooks are running smoothly and efficiently.

