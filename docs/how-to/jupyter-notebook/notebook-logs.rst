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


Conclusion
----------

Retrieving logs is a critical task for maintaining and troubleshooting Jupyter Notebooks in the DSS environment. This guide has shown you how to access logs quickly to help ensure your notebooks are running smoothly and efficiently.

