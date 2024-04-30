Access the Jupyter Notebooks UI
===============================

This guide explains how to access the user interface of a Jupyter Notebook running in the Data Science Stack (DSS) environment.

Overview
--------

Accessing the Jupyter Notebook UI allows you to interact directly with your notebooks, run code, and visualise data. This is done through a web browser by navigating to the URL associated with your active notebook.

Prerequisites
-------------

Ensure the following before attempting to access the Notebook UI:

- DSS CLI installed on your workstation.
- At least one notebook is currently active in the DSS environment.

Finding the Notebook URL
------------------------

1. **List active notebooks**:

   To find the URL of your Jupyter Notebook, first ensure that it is active. Run the `dss list` command to see all the notebooks and their statuses:

   .. code-block:: bash

       dss list

   Look for the notebook in the output, and specifically check the URL column. An active notebook will have a URL listed, which indicates it is ready for access.

   Example output:

   .. code-block:: none

       Name          Image                                               URL                      
       my-notebook   kubeflownotebookswg/jupyter-tensorflow-full:v1.8.0  http://10.152.183.164:80

2. **Access the Notebook UI**:

   Once you have the URL from the `dss list` command, open a web browser and enter the URL into the address bar. This will direct you to the Jupyter Notebook interface where you can start working with your notebook.

   Ensure that the notebook is in an active state. If the notebook is not active, you may need to start it or check for any issues that are preventing it from being accessible.

Conclusion
----------

Accessing the Jupyter Notebook UI through the DSS environment is straightforward once your notebook is active and running. This direct interaction with your notebooks facilitates a productive environment for developing and testing your data science projects.

