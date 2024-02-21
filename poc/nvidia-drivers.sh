#!/bin/bash
set -e

if nvidia-smi 1>/dev/null ; then
  echo "NVIDIA drivers are already installed."
else
  echo "Installing the NVIDIA drivers."
  sudo apt install -y nvidia-headless-535-server nvidia-utils-535-server
  sudo nvidia-smi
  echo "NVIDIA drivers installed and loaded successfully on host!"
fi
