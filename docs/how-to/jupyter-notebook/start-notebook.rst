Start a Notebook
================

This guide provides instructions on how to start a stopped Jupyter Notebook within the Data Science Stack (DSS) environment.

Overview
--------

A Jupyter Notebook that has been stopped can be restarted using the DSS command line interface (CLI). This allows you to resume your work without needing to configure a new notebook.

Prerequisites
-------------

Before starting a notebook, ensure you have the following:

- DSS CLI installed on your workstation.
- A stopped notebook. You can verify the status of notebooks using the ``dss list`` command.

Starting a Stopped Notebook
---------------------------

1. **List the available notebooks**:

   First, use the ``dss list`` command to display all notebooks and their statuses:

   .. code-block:: bash

       dss list

   Example output:

   .. code-block:: none

       Name          Image                                               URL       
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  (Stopped)

   This shows that ``my-notebook`` is currently stopped.

2. **Start the notebook**:

   To start the notebook, use the ``dss start`` command followed by the name of the notebook:

   .. code-block:: bash

       dss start my-notebook

   Expected output:

   .. code-block:: none

       Executing start command
       Starting the notebook my-notebook. Check `dss list` for the status of the notebook.

3. **Verify the notebook is running**:

   After initiating the start command, the notebook may go through statuses such as *Starting* or *Downloading*. To check the current status and access the URL once ready, run:

   .. code-block:: bash

       dss list

   Example output when the notebook is ready:

   .. code-block:: none

       Name          Image                                               URL                      
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

   This URL can be used to access your Jupyter Notebook.

Conclusion
----------

Starting a stopped notebook is a straightforward process with the DSS CLI. Once the notebook status changes to an active URL, you can continue your work directly from where you left off.

