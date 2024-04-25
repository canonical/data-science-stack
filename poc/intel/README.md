# Intel xGPU PoC

Launch Jupyter notebooks with Intel xGPU support enabled for Tensorflow
PyTorch, and OpenVINO. Note that MLFlow is also deployed along side Jupyter.

## Verify Intel xGPU Availablity

Running this PoC requires an Intel discreet or integrated GPU to be available
on your system in order to run. In cases where a system contains both a dGPU
and iGPU (e.g. NVIDIA discreet card with Intel iGPU), it is important to
verify that the Intel xGPU is visible to the OS. This can be done with a
command like:

```
$ lspci -nn | grep  -Ei 'VGA|DISPLAY'
```

## Application Details

Below are important notes about each application. 

* **itex (Tensorflow)**: pulls image directly from DockerHub; requires 8 GiB RAM.
* **ipex (PyTorch)**: pulls image directly from DockerHub; requires 16 GiB RAM.
* **OpenVINO**: requires a user to first build the Docker image locally (see
shell script in `openvino-image` folder), so Docker must be installed and
configured on the system; requires 8 GiB RAM.

## Limitations

This PoC assumes a single Intel xGPU on the system where it is run, so a user
cannot launch multiple applications simultaneously.