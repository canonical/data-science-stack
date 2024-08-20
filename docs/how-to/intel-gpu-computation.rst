.. _intel_calculations:

Running calculations with Intel frameworks
==========================================

This guide describes how to run simple calculations with machine learning frameworks on Intel hardware with DSS.

Prerequisites
-------------

* Your machine includes an Intel GPU.
* Ubuntu 22.04.
* Intel plugin is :ref:`enabled <enable_intel_gpu>` on your Kubernetes cluster.
* DSS is :ref:`installed <install_DSS_CLI>` and :ref:`initialised <initialise_DSS>`.
* Intel :ref:`IPEX/ITEX notebook is created <manage_notebooks>`.

Intel Pytorch Extension Notebook (IPEX)
---------------------------------------

First, :ref:`access a notebook <access_notebook>` in DSS.

After that, you can find an example machine learning workload for a computer vision task 
in the `Intel documentation <https://intel.github.io/intel-extension-for-pytorch/xpu/latest/tutorials/examples.html#float32>`_. 
Copy and paste the code into a notebook cell and run it.

Intel TensorFlow Extension Notebook (ITEX)
------------------------------------------

First, :ref:`access a notebook <access_notebook>` in DSS.

After that, you can find a recommended example for running a machine learning workload using Intel TensorFlow Extension (ITEX)
in the `Intel TensorFlow documentation <https://github.com/intel/intel-extension-for-tensorflow/blob/main/examples/quick_example.md>`_. 
Copy and paste the code into a notebook cell and run it.
