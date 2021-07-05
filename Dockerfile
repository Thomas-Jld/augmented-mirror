# FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04
FROM nvidia/cudagl:10.2-devel-ubuntu18.04

#CMD nvidia-smi
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /Miroir/

RUN apt-get update && \
  apt-get -y install python3-pip libusb-1.0-0-dev libgl1-mesa-glx nano git curl nodejs python3-apt

# RUN apt-get -y install python3.7
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install gdown

WORKDIR /Miroir/build

# RUN apt-get -y install g++ unzip zip openjdk-11-jdk 


RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc-8 g++-8 \
        ca-certificates \
        ffmpeg \
        wget \
        unzip \
        python3-dev \    
        python3-opencv \
        # python3-pip \
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


ARG BAZEL_VERSION=4.1.0
RUN mkdir /bazel && \
    wget --no-check-certificate -O /bazel/installer.sh "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/b\
azel-${BAZEL_VERSION}-installer-linux-x86_64.sh" && \
    wget --no-check-certificate -O  /bazel/LICENSE.txt "https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE" && \
    chmod +x /bazel/installer.sh && \
    /bazel/installer.sh  && \
    rm -f /bazel/installer.sh
    
# RUN gdown --id 1AfEjEcUwAb70QFfwiaje2d0QkNYYZv3x --output bazel-4.1.0-installer-linux-x86_64.sh
# RUN chmod +x bazel-4.1.0-installer-linux-x86_64.sh
# RUN ./bazel-4.1.0-installer-linux-x86_64.sh


RUN apt-get update
RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase
RUN apt-get -y install protobuf-compiler
RUN gdown --id 1Z9w1j_0m90XA7rA6XwIIi2JQPmMM3TMv --output mediapipe-0.8.3.1.zip
RUN unzip mediapipe-0.8.3.1.zip
WORKDIR /Miroir/build/mediapipe-0.8.3.1
RUN python3 -m pip install -r requirements.txt

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install libprotoc-dev
RUN export
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install --upgrade setuptools
RUN pip3 install wheel
RUN pip3 install future
RUN pip3 install six==1.14.0
RUN pip3 install tensorflow==1.14.0
RUN pip3 install tf_slim

# ENV ANDROID_NDK_HOME="/home"
# RUN export
# RUN chmod +x setup_android_sdk_and_ndk.sh
# RUN ./setup_android_sdk_and_ndk.sh

RUN python3 setup.py gen_protos

RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt-get update
RUN apt-get -y remove gcc
RUN apt-get -y install gcc-8 g++-8
RUN ln -s /usr/bin/gcc-8 /usr/bin/gcc

RUN add-apt-repository ppa:kisak/kisak-mesa
RUN apt-get update
RUN apt-get -y install mesa-utils
# RUN pip3 install mediapipe
RUN python3 setup.py install

WORKDIR /Miroir/build

COPY ./test.py .

# RUN python3 -m pip install sklearn setuptools
# ADD requirements.txt .
# RUN python3 -m pip install -r requirements.txt


# COPY . .

# #RUN git clone https://github.com/Thomas-Jld/detectron2 reflection/detectron2
# #RUN curl https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl --output reflection/models/model_final_162be9.pkl 
# #RUN	curl https://download.01.org/opencv/openvino_training_extensions/models/human_pose_estimation/checkpoint_iter_370000.pth --output reflection/pose-estimation/checkpoint_iter_370000.pth

# WORKDIR /Miroir/reflection/

# #RUN python3 -m pip install -e detectron2 

# CMD ./launch_reflection.sh
