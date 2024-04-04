# Proof of Concepts

The scripts in this folder are only intended as PoC cases. Their goal is to
only verify the architecture of DSS on different platforms.

## How to run

NOTE: You will need `sudo` privileges to be able to run this script

1. Go to the target folder
2. run the `deploy.sh` script
3. You can then interact with the system with `microk8s.kubectl`

You can also modify the manifests found in the corresponding 
`{nvidia,intel}/manifests` folders to play around with different
notebook setups.

**WARNING**: The `cleanup.sh` scripts are going to remove the whole microK8s cluster
