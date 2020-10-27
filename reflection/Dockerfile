FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

#CMD nvidia-smi

WORKDIR /reflection

COPY . .

RUN apt-get update && \
  apt-get -y install python3-pip libusb-1.0-0-dev libgl1-mesa-glx nano git curl && \
  pip3 install --upgrade pip && \
  pip3 install -r requirements.txt


RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase

WORKDIR /reflection/reflections-evaluation/ 

RUN rm -rf detectron2/; exit 0

RUN git clone https://github.com/Thomas-Jld/detectron2 && \
  python3 -m pip install -e detectron2 

RUN cp detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml configs/densepose_rcnn_R_50_FPN_s1x.yaml  && \
  cp detectron2/projects/DensePose/configs/Base-DensePose-RCNN-FPN.yaml configs/Base-DensePose-RCNN-FPN.yaml  && \
  curl https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl --output models/model_final_162be9.pkl
  
