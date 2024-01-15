#FROM ubuntu:22.10
FROM tensorflow/tensorflow:2.15.0-gpu
USER root

LABEL maintainer "Joao Victor Pinto <jodafons@cern.ch> and Micael Araujo <mverissi@cern.ch>"

ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV TERM screen
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive
#ENV CPU_N=$(grep -c ^processor /proc/cpuinfo)
ENV CPU_N=6

# update all packages
RUN apt-get update -y --fix-missing

# root dependencies
RUN apt-get install -y dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev \
libxft-dev libxext-dev python3 libssl-dev libafterimage0
#RUN apt-get install -y libtbb-dev dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev \
#libxft-dev libxext-dev python-is-python3 libssl-dev

# others
RUN apt-get install -y git gfortran libpcre3-dev \
xlibmesa-glu-dev libglew-dev libftgl-dev \
libmysqlclient-dev libfftw3-dev libcfitsio-dev \
graphviz-dev libavahi-compat-libdnssd-dev \
libldap2-dev python3-dev python3-numpy libxml2-dev libkrb5-dev \
libgsl0-dev qtwebengine5-dev nlohmann-json3-dev
#RUN apt-get install -y git gfortran libpcre3-dev \
#xlibmesa-glu-dev libglew-dev libftgl-dev \
#libmysqlclient-dev libfftw3-dev libcfitsio-dev \
#graphviz-dev libavahi-compat-libdnssd-dev \
#libldap2-dev libxml2-dev libkrb5-dev \
#libgsl0-dev qtwebengine5-dev

# Installing cmake3
WORKDIR /usr
#RUN wget --progress=dot:giga https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-linux-x86_64.sh -P /usr/

RUN wget --progress=dot:giga https://cmake.org/files/v3.19/cmake-3.19.7-Linux-x86_64.sh -P /usr/
RUN chmod 755 cmake-3.19.7-Linux-x86_64.sh
RUN ./cmake-3.19.7-Linux-x86_64.sh --skip-license

#RUN chmod 755 cmake-3.28.1-linux-x86_64.sh
#RUN ./cmake-3.28.1-linux-x86_64.sh --skip-license
RUN apt-get update && apt-get install -y texlive-full



WORKDIR /apt
# install ROOT
RUN git clone https://github.com/root-project/root.git
RUN cd root && git checkout -b v6-31-01 v6-31-01
RUN cd root && mkdir buildthis && cd buildthis && cmake -DPYTHON_EXECUTABLE=/usr/bin/python -Dimt=ON -Dxrootd=OFF -Dbuiltin_xrootd=OFF .. && make -j$CPU_N
ENV ROOTSYS "/apt/root/buildthis/"
ENV PATH "$ROOTSYS/bin:$PATH"
ENV LD_LIBRARY_PATH "$ROOTSYS/lib:$LD_LIBRARY_PATH"
ENV PYTHONPATH "/apt/root/buildthis/lib:$PYTHONPATH"

RUN pip install --upgrade pip
RUN pip install virtualenv

COPY requirements.txt /
RUN cd / && pip install --ignore-installed -r requirements.txt 
RUN rm /requirements.txt
RUN echo "source /apt/root/buildthis/bin/thisroot.sh" >> /setup_envs.sh
