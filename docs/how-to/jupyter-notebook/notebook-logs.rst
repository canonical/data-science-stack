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

       Logs for my-notebook:
       [logs]

Conclusion
----------

Retrieving logs is a critical task for maintaining and troubleshooting Jupyter Notebooks in the DSS environment. This guide has shown you how to access logs quickly to help ensure your notebooks are running smoothly and efficiently.

