
.. _home:

Data Science Stack documentation
================================

Data Science Stack (DSS) is a ready-to-run environment for Machine Learning (ML) and data science.  
It's built on open-source tooling, including Canonical K8s, JupyterLab, and MLflow, and is usable on any Ubuntu/Snap-enabled workstation.

DSS provides a Command Line Interface (CLI) for managing containerised ML environment images such as PyTorch or TensorFlow, on top of Canonical K8s.

Typically, creating ML environments on a workstation involves complex and hard-to-reverse configurations. 
DSS solves this problem by providing accessible, production-ready, isolated, and reproducible ML environments that fully utilise a workstation's GPUs.

Both ML beginners and engineers who need to build complex development and runtime environments will see set-up time reduced to a minimum, 
allowing them to get started with meaningful work within minutes.

---------

In this documentation
---------------------

..  grid:: 1 1 2 2

   ..  grid-item:: :doc:`Tutorial <tutorial/index>`

       Get started - a hands-on introduction to DSS for newcomers

   ..  grid-item:: :doc:`How-to guides <how-to/index>`

      Step-by-step guides covering key operations and common tasks with DSS

.. grid:: 1 1 2 2

   .. grid-item:: :doc:`Explanation <explanation/index>`

      Discussion and clarification of key topics

---------

Project and community
---------------------

Data Science Stack is an open-source project that values its community. We warmly welcome contributions, suggestions, fixes, and constructive feedback from everyone.

* Read our `Code of conduct`_.
* `Contribute`_ and `report bugs <https://github.com/canonical/data-science-stack/issues/new/choose>`_.
* Join the `Discourse forum`_.
* Talk to us on `Matrix`_.

.. toctree::
   :hidden:
   :maxdepth: 2

   Home <self>
   tutorial/index
   How to <how-to/index>
   explanation/index
