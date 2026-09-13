# Dockerfile for the DATASCI 350 final project.
#
# A Dockerfile is a recipe. Each instruction below adds one layer to the
# image. When you run "docker build", Docker follows this recipe from top
# to bottom and produces an image that contains Ubuntu, Python, Quarto,
# and your project files.
#
# The comments explain every step. Read them once, then change only the
# parts you need to change.

# ---------------------------------------------------------------------
# 1. Base image
# ---------------------------------------------------------------------
# FROM chooses the starting point. We start from Ubuntu 24.04, the same
# system you saw in the containers lecture.
# We pin the tag to "24.04" rather than "latest". "latest" changes over
# time, and a base image that changes breaks reproducibility.
FROM ubuntu:24.04

# ---------------------------------------------------------------------
# 2. Build-time settings
# ---------------------------------------------------------------------
# DEBIAN_FRONTEND=noninteractive stops apt-get from asking questions
# during the build. Nobody is at the keyboard to answer them.
ENV DEBIAN_FRONTEND=noninteractive

# Use bash for the RUN steps below. Docker uses the simpler "sh" shell by
# default, and bash supports more of the syntax you already know.
SHELL ["/bin/bash", "-c"]

# ---------------------------------------------------------------------
# 3. System packages
# ---------------------------------------------------------------------
# apt-get update refreshes the list of available packages.
# apt-get install -y installs without asking for confirmation.
# --no-install-recommends skips optional extras and keeps the image small.
# We do not pin apt versions here. Ubuntu replaces a package's exact
# version whenever it ships a security fix, and a pinned version that
# no longer exists stops the build. The base image tag and the Python
# packages in requirements.txt carry the pins instead.
# The final "apt-get clean" and "rm -rf" delete the download cache, which
# would otherwise sit inside the image for no reason.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    git \
    python3.12 \
    python3.12-venv \
    python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------
# 4. Quarto
# ---------------------------------------------------------------------
# Quarto is not in the Ubuntu package list, so we download the .deb file
# from GitHub and install it. The version 1.10.18 is written out in full,
# so the image you build is the image everyone else builds.
# Laptops use different processor architectures: Apple Silicon Macs are
# arm64, most Windows and Linux machines are amd64. The command
# "dpkg --print-architecture" reports which one this build is running on,
# so the same Dockerfile works for everyone in the class.
RUN ARCH=$(dpkg --print-architecture) && \
    wget -q "https://github.com/quarto-dev/quarto-cli/releases/download/v1.10.18/quarto-1.10.18-linux-${ARCH}.deb" && \
    apt-get update && \
    apt-get install -y --no-install-recommends ./quarto-1.10.18-linux-${ARCH}.deb && \
    rm quarto-1.10.18-linux-${ARCH}.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------
# 5. Python environment
# ---------------------------------------------------------------------
# Ubuntu protects its own Python installation, so we create a virtual
# environment at /opt/venv and install our packages there.
RUN python3 -m venv /opt/venv

# PATH tells the shell where to look for programs. Putting /opt/venv/bin
# first means "python" and "pip" refer to the virtual environment,
# without activating it by hand in every later step.
ENV PATH="/opt/venv/bin:$PATH"

# We copy requirements.txt on its own, before the rest of the project.
# Docker caches each layer. As long as requirements.txt is unchanged,
# rebuilds skip this slow install step even after you edit your report.
COPY requirements.txt /project/requirements.txt
RUN pip install --no-cache-dir -r /project/requirements.txt

# ---------------------------------------------------------------------
# 6. Project files
# ---------------------------------------------------------------------
# WORKDIR sets the folder that later instructions run inside.
WORKDIR /project

# Copy everything else from your repository into the image, including
# report.qmd and the saved data snapshot in data/raw/.
# The .dockerignore file next to this one lists what stays out.
COPY . /project

# ---------------------------------------------------------------------
# 7. Default command
# ---------------------------------------------------------------------
# CMD is what runs when someone types "docker run" without extra
# arguments. Here it renders your report and then copies the result into
# /project/output, which the README mounts to a folder on your own
# computer so that you can open the report.
#
# We render first and copy afterwards, rather than rendering straight into
# output/. Quarto clears its output folder before writing, and it cannot
# clear a folder that Docker has mounted from outside.
#
# QUARTO_PYTHON points Quarto at the virtual environment's Python.
ENV QUARTO_PYTHON=/opt/venv/bin/python
CMD ["bash", "-c", "quarto render report.qmd && mkdir -p output && cp -a report.html output/ && echo 'Rendered report is in output/report.html'"]
