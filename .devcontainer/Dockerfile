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
    