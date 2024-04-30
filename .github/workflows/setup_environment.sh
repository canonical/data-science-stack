#!/bin/bash

# Python setup
apt-get update -yqq
apt-get install -yqq python3-pip
pip3 install tox

# Microk8s setup
snap install microk8s --channel=1.28/stable --classic
usermod -a -G microk8s $USER
mkdir -p /home/$USER/.kube
chown -f -R $USER /home/$USER/.kube
newgrp microk8s