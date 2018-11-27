# Build in the root of the repo after building pkg/docker/linux-build/Dockerfile
# Expected usage (from root of repo):
#    docker build -t smartva-dev -f pkg/docker/dev/Dockerfile .
#    docker run -it --rm -v `pwd`:/home/smartva/smartva smartva-dev
FROM smartva-build-linux

USER root

COPY requirements*.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements-dev.txt \
    && rm /tmp/requirements*.txt \
    && python -c 'import matplotlib.pyplot'

USER smartva

ENTRYPOINT [ "/bin/bash" ]
