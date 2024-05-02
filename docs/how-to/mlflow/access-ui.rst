Access the MLFlow UI
===============================

This guide explains how to access the user interface of MLFlow in the Data Science Stack (DSS) environment.

Overview
--------

Accessing the MLFlow UI allows you to interact directly with your Experiments and Models. This is done through a web browser by navigating to the URL associated with MLFlow.

Prerequisites
-------------

Ensure the following before attempting to access the MLFlow UI:

- DSS CLI installed on your workstation.
- MLFlow deployment is `Ready`.

Finding the MLFlow URL
------------------------

1. **Get the MLFlow URL**:

   To find the URL of MLFlow, run the `dss status` command:

   .. code-block:: bash

       dss status

   Look for the `MLFlow URL` in the output.

   Example output:

   .. code-block:: none

        [INFO] MLFlow deployment: Ready
        [INFO] MLFlow URL: http://10.152.183.205:5000
        [INFO] GPU acceleration: Disabled

2. **Access the MLFlow UI**:

   Once you have the URL from the `dss status` command, open a web browser and enter the URL into the address bar. This will direct you to the MLFlow interface where you can start working with your models.


Conclusion
----------

Accessing the MLFlow UI through the DSS environment is straightforward once your MLFlow deployment is active and running.
