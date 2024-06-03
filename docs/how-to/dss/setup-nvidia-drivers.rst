.. _setup-nvidia-drivers:

Setup NVIDIA Drivers
==============

This guide explains how to setup the NVIDIA drivers in your DSS environment.

Overview
--------
To ensure the DSS can utilize the NVIDIA GPUs in a machine:

1. The host will need to have the NVIDIA drivers installed
2. MicroK8s will need to be setup to utilise those drivers

MicroK8s is leveraging the `NVIDIA Operator`_ to for setting up and
configuring the NVIDIA runtime. The NVIDIA Operator will also install
the NVIDIA drivers, if they are not present already on the host machine.

Enable the NVIDIA runtimes on MicroK8s
----------------------------------
To enable the NVIDIA runtimes on MicroK8s run the following
command:

.. code-block:: bash

   sudo microk8s enable gpu


.. note::
   The NVIDIA Operator will detect if the NVIDIA drivers are not present at all
   and will install them in this case. But the NVIDIA Operator can also detect
   if you have drivers already installed. In this case the NVIDIA Operator will
   use the host's drivers.

