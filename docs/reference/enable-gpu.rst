Enable Nvidia GPUs
==================

To be able to run workloads on GPU with DSS, you need to have:

* NVIDIA drivers installed on your machine.
* The MicroK8s runtime configured to be able to use the Nvidia drivers.

The `MicroK8s GPU add-on`_ is installing the NVIDIA Operator. The NVIDIA operator can either install or detect the NVIDIA drivers if they are already present on the host machine.

Before installing DSS:

1. Follow the MicroK8s documentation to `Install MicroK8s`_.

2. Enable MicroK8s GPU add-on.

   .. code-block:: bash

     microk8s enable gpu

3. Wait for GPU operator components to be ready. This can take around 5 minutes.

   .. code-block:: bash

     while ! sudo microk8s.kubectl logs -n gpu-operator-resources -l app=nvidia-operator-validator | grep "all validations are successful"
     do
       echo "waiting for validations"
       sleep 5
     done

4. Run `dss status` to check that GPU acceleration is enabled.

   .. code-block:: bash

     dss status

   Expected output:
    
   .. code-block:: bash

     [INFO] MLflow deployment: Not ready
     [INFO] GPU acceleration: Enabled (NVIDIA-GeForce-RTX-3070-Ti)

   .. note::
        
     the GPU model `NVIDIA-GeForce-RTX-3070-Ti` will be different depending on your device.
