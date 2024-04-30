Stop a Notebook
===============

This guide provides instructions on how to stop a running Jupyter Notebook within the Data Science Stack (DSS) environment.

Overview
--------

Stopping a Jupyter Notebook that is in use helps free up resources and ensures data safety when not actively working on the notebook. This guide covers the process of stopping a notebook using the DSS command line interface (CLI).

Prerequisites
-------------

Before stopping a notebook, ensure you have the following:

- DSS CLI installed on your workstation.
- A running notebook. You can verify the status of notebooks using the ``dss list`` command.

Stopping a Running Notebook
---------------------------

1. **List the available notebooks**:

   Use the ``dss list`` command to display all notebooks and their current statuses:

   .. code-block:: bash

       dss list

   Example output might show a running notebook:

   .. code-block:: none

       Name          Image                                               URL                      
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80 

2. **Stop the notebook**:

   To stop a running notebook, use the ``dss stop`` command followed by the name of the notebook:

   .. code-block:: bash

       dss stop my-notebook

   Expected output:

   .. code-block:: none

       Stopping the notebook my-notebook. Check `dss list` for the status of the notebook.

3. **Verify the notebook has stopped**:

   After initiating the stop command, the notebook will go through a "Stopping" state. To confirm the notebook has stopped, run the `dss list` command again:

   .. code-block:: bash

       dss list

   Example output when the notebook is stopped:

   .. code-block:: none

       Name          Image                                               URL       
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  (Stopped)

Conclusion
----------

Stopping a notebook when it's no longer in use is crucial for managing resources efficiently in the DSS environment. By following these steps, you can ensure that your notebook is safely stopped and ready to be started again when needed.

