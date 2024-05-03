Enable Nvidia GPUs
==================

To be able to run workloads on GPU with DSS, you need to have NVIDIA drivers installed on your machine. This can be done using `MicroK8s GPU add-on`_.

Before installing DSS:

1. Follow the MicroK8s documentation to `Install MicroK8s`_.

2. Enable MicroK8s add-ons, including GPU.

    .. code-block:: bash

        microk8s enable storage dns rbac gpu

3. Wait for GPU operator components to be ready. This can take around 5 minutes.

    .. code-block:: bash

        while ! sudo microk8s.kubectl logs -n gpu-operator-resources -l app=nvidia-operator-validator | grep "all validations are successful"
        do
          echo "waiting for validations"
          sleep 5
        done

4. Install DSS snap and initialise.

    .. code-block:: bash
 
        microk8s config > ~/.dss/config
        sudo snap install data-science-stack
        dss initialize
