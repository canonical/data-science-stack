Access your data from DSS
=========================

This guide provides instructions on how to access the stored data from your Notebooks in the Data Science Stack (DSS) environment.

Overview
--------
Accessing your data is useful when you want to browse or modify the files stored from your Notebooks. 

Prerequisites
-------------
Before accessing your data, ensure you have the following:

- DSS CLI installed on your workstation.
- At least one notebook was created in the DSS environment.

Accessing your data
-------------------
By default, your Notebooks data will be stored in a directory under `/var/snap/microk8s/common/default-storage`:

* `Microk8s hostpath docs`_

This directory is shared by all DSS Notebooks.

1. **Find the directory of your stored data**
    To find the directory containing your Notebooks data, list the directories under `/var/snap/microk8s/common/default-storage`:

    .. code-block:: bash

        ls /var/snap/microk8s/common/default-storage/

    
    Expected output:

    .. code-block:: bash

        dss-notebooks-pvc-00037e23-e2e2-4ab4-9088-45099154da30

    The storage directory is the one prefixed with `dss-notebooks-pvc` as shown in the output. Note that the characters that follow will not be the same for all DSS environments.

2. **Access your Notebooks data**
    From your local file browser, navigate to the folder `/var/snap/microk8s/common/default-storage/[directory name]`. Use the directory name you got from the previous step.

    Now, you can view and manage all your stored Notebooks data.

Conclusion
----------
Accessing the DSS Notebooks data is straightforward once you have created a Notebook. This direct interaction with your Notebooks data facilitates a productive environment for managing the files used in your data science projects.