Delete a Notebook
=================

This guide provides instructions on how to remove a Jupyter Notebook from the Data Science Stack (DSS) environment.

Overview
--------

Deleting a Jupyter Notebook is useful when you no longer need the notebook and want to clear up resources or declutter your workspace. This process is handled through the DSS command line interface (CLI), and it is non-blocking, meaning you can continue other work while the deletion completes.

.. note::

   When you delete a notebook, any data stored under `~/shared` within the notebook will be preserved and remain accessible to other notebooks. This shared storage is designed to ensure that valuable data is not lost even when individual notebooks are removed from the environment.

Prerequisites
-------------

Before deleting a notebook, ensure you have the following:

- DSS CLI installed on your workstation.
- The notebook you wish to delete.

Deleting a Notebook
-------------------

1. **Check the existing notebooks**:

   Before deletion, verify the notebook you want to delete is listed and check its status with the `dss list` command:

   .. code-block:: bash

       dss list

   Example output:

   .. code-block:: none

       Name          Image                                               URL                       
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

2. **Remove the notebook**:

   To delete the notebook, use the `dss remove` command followed by the name of the notebook:

   .. code-block:: bash

       dss remove my-notebook

   Expected output:

   .. code-block:: none

       Removing the notebook my-notebook. Check `dss list` for the status of the notebook.

3. **Verify the notebook has been removed**:

   After initiating the remove command, the notebook may go through a "Removing" state. To confirm the notebook has been removed, run the `dss list` command again:

   .. code-block:: bash

       dss list

   If the notebook has been successfully removed, it will no longer appear in the list. If it's still showing as "Removing", you may need to wait a bit longer or investigate if there are any issues preventing the deletion.

Conclusion
----------

Deleting a notebook effectively frees up resources and helps maintain an organised environment. This guide has outlined how to safely remove a notebook from your DSS setup, ensuring you can manage your workspace efficiently.
