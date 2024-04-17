#!/bin/bash

docker build \
  -t local/openvinotoolkit:mainbranch \
  github.com/openvinotoolkit/openvino_notebooks

render_gid=$(getent group render | cut -d: -f3)
container_user=$(docker run --rm local/openvinotoolkit:mainbranch /usr/bin/whoami)

docker build \
  -t local/openvinotoolkit:render-addon . \
  --build-arg render_gid=${render_gid} \
  --build-arg container_user=${container_user}
