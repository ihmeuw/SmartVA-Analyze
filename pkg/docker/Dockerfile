FROM buildpack-deps:jessie

ENV WINEDEBUG=-all

RUN apt-get update && apt-get install -y --no-install-recommends \
        apt-transport-https \
        build-essential \
        curl \
        git \
        make \
        openssh-server \
        sudo \
        vim \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN dpkg --add-architecture i386 \
    && cd /tmp \
    && wget https://dl.winehq.org/wine-builds/Release.key \
    && apt-key add Release.key \
    && echo "deb https://dl.winehq.org/wine-builds/debian/ jessie main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        cabextract \
        winehq-devel \
        Xvfb \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHON2_VERSION 2.7.12
ENV WINEARCH win32
ENV WINEPREFIX /home/smartva/.wine

EXPOSE 22
EXPOSE 8000

WORKDIR /home/smartva

# Use COPY here because Jenkins appears to have an old version of docker and can't expand .tar files.
COPY ssh.tar /home/smartva/
COPY run_tests_and_build_in_wine.patch /home/smartva/
COPY smartva-password.md5 /home/smartva/

RUN groupadd -r smartva \
    && useradd -r -g smartva smartva -s /bin/bash \
    && tar -xf ssh.tar \
    && cp -R /etc/skel/. /home/smartva \
    && chown -R smartva:smartva /home/smartva \
    && chpasswd -e < smartva-password.md5 \
    && mkdir /var/run/sshd

USER smartva

RUN wine wineboot --init \
    && git clone -b develop ssh://git@stash.ihme.washington.edu:7999/va/smartva.git \
    && cp -r smartva/pkg/build-agent/ build-agent/ \
    && git apply run_tests_and_build_in_wine.patch \
    && wget https://www.python.org/ftp/python/${PYTHON2_VERSION}/python-${PYTHON2_VERSION}.msi \
    && wine msiexec /i python-${PYTHON2_VERSION}.msi ALLUSERS=1 \
    && wget https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi \
    && wine msiexec /i VCForPython27.msi \
    && wget http://superb-sea2.dl.sourceforge.net/project/wxpython/wxPython/3.0.2.0/wxPython3.0-win32-3.0.2.0-py27.exe \
    && ( Xvfb :0 -screen 0 1024x768x16 & ) \
    && export DISPLAY=:0.0 \
    && wine wxPython3.0-win32-3.0.2.0-py27.exe /sp- /verysilent /norestart /SUPPRESSMSGBOXES \
    && wine python -m pip install -r smartva/requirements.txt \
    && echo "export WINEDEBUG=$WINEDEBUG" >> ~/.profile \
    && ln -s ~/smartva ~/build-agent/smartva \
    && rm * | true

USER root

CMD ["/usr/sbin/sshd", "-D"]
