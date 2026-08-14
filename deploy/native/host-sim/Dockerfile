FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ENV container=docker

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        iproute2 \
        openssh-server \
        procps \
        socat \
        sudo \
        systemd \
        systemd-sysv \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash --groups sudo omerta \
    && passwd -l omerta \
    && printf 'omerta ALL=(ALL) NOPASSWD:ALL\n' >/etc/sudoers.d/90-omerta-n0 \
    && chmod 0440 /etc/sudoers.d/90-omerta-n0 \
    && install -d -m 0750 -o root -g root /etc/omertaos \
    && install -d -m 0755 -o root -g root /var/lib/omertaos-n0

COPY deploy/native/host-sim/omertaos-n0-sim.service /etc/systemd/system/omertaos-n0-sim.service
COPY deploy/native/host-sim/bootstrap.sh /usr/local/sbin/omertaos-n0-sim-bootstrap
COPY deploy/native/host-sim/check.sh /usr/local/sbin/omertaos-n0-sim-check

RUN chmod 0755 /usr/local/sbin/omertaos-n0-sim-bootstrap /usr/local/sbin/omertaos-n0-sim-check \
    && systemctl enable omertaos-n0-sim.service ssh.service \
    && systemctl mask systemd-logind.service getty@.service console-getty.service

STOPSIGNAL SIGRTMIN+3
EXPOSE 22
CMD ["/sbin/init"]
