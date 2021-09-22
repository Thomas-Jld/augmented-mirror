FROM nvidia/cudagl:10.2-devel-ubuntu18.04

#CMD nvidia-smi
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc-8 g++-8 \
        ca-certificates \
        ffmpeg \
        wget \
        unzip \
        python3.7 \
        python3.7-dev \    
        python3-pip \
        python3-opencv \
        python3-apt \
        libopencv-core-dev \
        libopencv-highgui-dev \
        libopencv-imgproc-dev \
        libopencv-video-dev \
        libopencv-calib3d-dev \
        libopencv-features2d-dev \
        software-properties-common && \
    add-apt-repository -y ppa:openjdk-r/ppa && \
    apt-get update && apt-get install -y openjdk-8-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /Miroir/

RUN apt-get update && apt-get -y install libusb-1.0-0-dev libgl1-mesa-glx nano git curl

# Installing python requirements

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install setuptools
RUN python3 -m pip install sklearn
ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install gdown

# Installing bazel and tools

WORKDIR /Miroir/build

ARG BAZEL_VERSION=4.1.0
RUN mkdir /bazel && \
    wget --no-check-certificate -O /bazel/installer.sh "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/b\
azel-${BAZEL_VERSION}-installer-linux-x86_64.sh" && \
    wget --no-check-certificate -O  /bazel/LICENSE.txt "https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE" && \
    chmod +x /bazel/installer.sh && \
    /bazel/installer.sh  && \
    rm -f /bazel/installer.sh

RUN apt-get update
RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase
RUN apt-get -y install protobuf-compiler

# Setting up the building folder

RUN gdown --id 1Z9w1j_0m90XA7rA6XwIIi2JQPmMM3TMv --output mediapipe-0.8.3.1.zip
RUN unzip mediapipe-0.8.3.1.zip
WORKDIR /Miroir/build/mediapipe-0.8.3.1
RUN python3 -m pip install -r requirements.txt

# Quick fixes

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install libprotoc-dev
RUN export
RUN ln -s /usr/bin/python3 /usr/bin/python

# Fixing python

WORKDIR /usr/lib/python3/dist-packages/gi
RUN ln -s _gi.cpython-36m-x86_64-linux-gnu.so _gi.cpython-37m-x86_64-linux-gnu.so

WORKDIR /usr/lib/python3/dist-packages
RUN ln -s apt_pkg.cpython-36m-x86_64-linux-gnu.so apt_pkg.so

# Building mediapipe

WORKDIR /Miroir/build/mediapipe-0.8.3.1

RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt-get update
RUN apt-get -y remove gcc
RUN apt-get -y install gcc-8 g++-8
RUN ln -s /usr/bin/gcc-8 /usr/bin/gcc

RUN add-apt-repository ppa:kisak/kisak-mesa
RUN apt-get update
RUN apt-get -y install mesa-utils
RUN python3 setup.py gen_protos
RUN python3 setup.py install

WORKDIR /Miroir

# Copying and launching the backend

COPY . .

WORKDIR /Miroir/reflection/

CMD ./launch_reflection.sh
