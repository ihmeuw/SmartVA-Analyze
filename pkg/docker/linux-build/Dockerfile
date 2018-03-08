FROM python:2.7.13-wheezy

COPY smartva-password.md5 /home/smartva/

RUN groupadd -r smartva \
    && useradd -r -g smartva smartva -s /bin/bash \
    && cp -R /etc/skel/. /home/smartva \
    && mkdir -p /home/smartva/.local/share \
    && chown -R smartva:smartva /home/smartva \
    && chpasswd -e < /home/smartva/smartva-password.md5 \
    && mkdir /var/run/sshd \
    && mkdir /tmp/.X11-unix \
    && chmod a+rwxt /tmp/.X11-unix \
    && echo "umask 002" >> /home/smartva/.bashrc

EXPOSE 22
EXPOSE 8000

VOLUME [ "/home/smartva/smartva" ]

USER smartva

WORKDIR /home/smartva/smartva

ENTRYPOINT [ "/bin/bash" ]

ENV WINE=""
ENV BUILD_SPECS="cli"

CMD ["/home/smartva/smartva/pkg/docker/run_docker_build.sh"]
