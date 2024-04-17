FROM local/openvinotoolkit:mainbranch

USER root

ARG render_gid
RUN groupadd -g "$render_gid" renderhost
ARG container_user
RUN usermod -aG renderhost "$container_user"

USER "$container_user"
