FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y python3.11 python3.11-venv python3-pip pipx && \
    curl -sL https://deb.nodesource.com/setup_20.x -o /tmp/nodesetup.sh && bash /tmp/nodesetup.sh && apt install -y nodejs

RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o /tmp/awscliv2.zip && \
    unzip /tmp/awscliv2.zip -d /tmp && \
    /tmp/aws/install

RUN curl https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip -o /tmp/terraform.zip && \
    unzip /tmp/terraform.zip -d /usr/local/bin

USER vscode
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    /home/vscode/.local/bin/poetry self add poetry-plugin-lambda-build

USER root

RUN curl -SsL https://downloads.gauge.org/stable | sh

RUN apt update \
     && apt install -y wget gnupg ca-certificates \
     && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/chrome.gpg \
     && sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
     && apt update \
     && apt install -y google-chrome-stable

ENV NPM_CONFIG_PREFIX=/home/gauge/.npm-packages
ENV PATH="${NPM_CONFIG_PREFIX}/bin:${PATH}"

ENV TAIKO_BROWSER_ARGS=--no-sandbox,--start-maximized,--disable-dev-shm-usage
ENV headless_chrome=true
ENV TAIKO_SKIP_DOCUMENTATION=true
