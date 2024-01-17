FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel
USER root

LABEL maintainer "Micael Araujo <mverissi@cern.ch> and Joao Victor Pinto <jodafons@cern.ch>"

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV TERM screen
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive
 
RUN apt-get update && apt-get install -y git
RUN apt-get install msttcorefonts -qq
RUN apt-get install -y texlive-full

ARG CONDA_PYTHON_VERSION=3
ARG CONDA_DIR=/opt/conda

# Instal basic utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends git wget unzip bzip2 build-essential ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN conda init
