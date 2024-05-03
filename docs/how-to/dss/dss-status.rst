Get Status of DSS
=================

This guide explains how to check the status of your DSS environment.

Overview
--------

The `dss status` command provides a quick way to check the status of your DSS environment, including the status of MLflow and whether a GPU is detected in the environment.

Installing the DSS Snap
-----------------------

To see the status of DSS, run the following command:

.. code-block:: bash

    dss status

If you have a DSS environment running and no GPU available, the expected output is:

.. code-block:: none

    [INFO] MLflow deployment: Ready
    [INFO] MLflow URL: http://10.152.183.68:5000
    [INFO] GPU acceleration: Disabled
