FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

#CMD nvidia-smi

WORKDIR /Miroir/

COPY . .

RUN apt-get update && \
  apt-get -y install python3-pip libusb-1.0-0-dev libgl1-mesa-glx nano git curl && \
  pip3 install --upgrade pip && \
  pip3 install -r requirements.txt


RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase

WORKDIR /Miroir/reflection/

RUN  python3 -m pip install -e detectron2 
