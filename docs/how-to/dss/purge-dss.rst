Purge DSS
===========

This guide explains how to purge (remove) the Data Science Stack (DSS) environment from your MicroK8s cluster

Overview
--------

The `dss purge` command provides a way to remove everything deployed by DSS from your MicroK8s cluster. This includes all the DSS components, such MLflow and Jupyter Notebooks.

.. note::

    This action removes the components of the DSS environment, but it does not remove the DSS CLI or your MicroK8s cluster.  To remove those, remove their snaps.

Prerequisites
-------------

This guide applies if you have the following:

- DSS initialized on your system.

Purging the DSS Environment
---------------------------

To purge all DSS components from your machine, do:

.. code-block:: bash

    dss purge

This will remove:
* all Jupyter Notebooks
* the MLflow server
* any data stored within the DSS environment

.. caution::

    This action is irreversible. All data stored within the DSS environment will be lost.

The expected output from the above command is:

.. code-block:: none

    [INFO] Waiting for namespace dss to be deleted...
    [INFO] Success: All DSS components and notebooks purged successfully from the Kubernetes cluster.

Conclusion
----------

All elements of the DSS environment have been purged from your MicroK8s cluster. You can now reinitialize DSS on your system if you wish to continue using it.
