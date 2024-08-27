.. _manage_MLflow:

Manage MLflow
=============

This guide describes how to manage `MLflow <Charmed MLflow_>`_ within your Data Science Stack (DSS) environment.

MLflow is a platform for managing the end-to-end machine learning life cycle. 
It includes tracking experiments, packaging code into reproducible runs, and sharing and deploying models.

.. _access_mlflow:

Access MLflow
-------------

You can access the MLflow User Interface (UI) within your Data Science Stack (DSS) environment through a web browser, 
by navigating to the URL associated with MLflow.
This UI allows you to interact directly with your MLflow experiments and models. 

1. **Get the MLflow URL**:

To find the URL of MLflow, run:

.. code-block:: bash

    dss status

Look for the MLflow URL in the output.
For example:

.. code-block:: none

    MLflow deployment: Ready
    MLflow URL: http://10.152.183.205:5000

.. note::

    To access the UI, your MLflow deployment should be `Ready`.        

2. **Access the MLflow UI**:

Once you know the URL, open a web browser and enter the URL into the address bar. 
This will direct you to the MLflow interface.

Get MLflow logs
---------------

You can retrieve logs for MLflow within your Data Science Stack (DSS) environment. 
Retrieving logs is a critical task for maintaining and troubleshooting MLflow.

To get MLflow logs, use the ``dss logs`` command with the ``--mlflow`` option:

.. code-block:: bash

    dss logs --mlflow

You should expect an output like this:

.. code-block:: none

    Logs for mlflow-6bbfc5db5-xlfvj:
    [2024-04-30 07:57:54 +0000] [22] [INFO] Starting gunicorn 20.1.0
    [2024-04-30 07:57:54 +0000] [22] [INFO] Listening at: http://0.0.0.0:5000 (22)
    [2024-04-30 07:57:54 +0000] [22] [INFO] Using worker: sync
    [2024-04-30 07:57:54 +0000] [23] [INFO] Booting worker with pid: 23
    [2024-04-30 07:57:54 +0000] [24] [INFO] Booting worker with pid: 24
    [2024-04-30 07:57:54 +0000] [25] [INFO] Booting worker with pid: 25
    [2024-04-30 07:57:54 +0000] [26] [INFO] Booting worker with pid: 26


Get MLflow artefacts
--------------------

MLflow artefacts, including `models <https://mlflow.org/docs/latest/models.html>`_, `experiments <https://mlflow.org/docs/latest/tracking.html#experiments>`_ and `runs <https://mlflow.org/docs/latest/tracking.html#runs>`_ are stored within your DSS environment.
They can be accessed and downloaded from the :ref:`MLflow UI <access_mlflow>`. 

See also
--------

* To learn how to manage your DSS environment, check :ref:`manage_DSS`. 
* If you are interested in managing Jupyter Notebooks within your DSS environment, see :ref:`manage_notebooks`.
* See `Charmed MLflow`_ for more details on MLflow.

