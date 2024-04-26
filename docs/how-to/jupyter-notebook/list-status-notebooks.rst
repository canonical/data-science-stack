List Created Notebooks
======================

This guide explains how to use the `dss list` command to view the current status of all notebooks within the Data Science Stack (DSS) environment.

Overview
--------

The `dss list` command provides a snapshot of all notebooks along with their current states. Understanding these states helps you manage and interact with your notebooks effectively.

Using the `dss list` Command
----------------------------

To view the list and status of all notebooks, run the following command in your DSS environment:

.. code-block:: bash

    dss list

This will display each notebook along with its current state and URL if applicable.

Notebook States
---------------

Each notebook can be in one of the following states:

- **Active**: The notebook is running and accessible. The URL under the "URL" column will be displayed, allowing you to access the notebook directly.

- **Stopped**: The notebook is not running. You can start it using the `dss start` command.

- **Stopping**: The notebook is in the process of stopping. It is advisable to wait until the process completes, transitioning to "Stopped".

- **Starting**: The notebook is starting up. This state indicates that the notebook is initializing and will soon be active.

- **Downloading**: The notebook is downloading necessary data or software. This is usually a transient state before it becomes "Active".

- **Removing**: The command to remove the notebook has been issued (`dss remove`), but the notebook has not been completely removed yet. This state will eventually clear once the notebook is fully removed.

Example Output
--------------

Here is an example of what you might see when running the `dss list` command:

.. code-block:: none

    Name          Image                                               URL                      
    my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80  (Active)
    data-prep     kubeflownotebookswg/jupyter-minimal:v1.5.0          (Downloading)
    test-env      kubeflownotebookswg/jupyter-scipy-notebook:v1.9.0   (Stopping)

Conclusion
----------

Understanding and utilising the `dss list` command is crucial for effective notebook management in the DSS environment. This command helps monitor and manage the state of your notebooks, ensuring you can access, start, or stop them as needed.

