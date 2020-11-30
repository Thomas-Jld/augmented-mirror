delete:
	sudo nvidia-docker image rm -f nvidia-cuda-test

clear:
	sudo nvidia-docker container prune

build:
	git clone https://github.com/Thomas-Jld/detectron2 reflection-evaluation/detectron2
	curl https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl --output reflection-evaluation/models/model_final_162be9.pkl
	curl  https://download.01.org/opencv/openvino_training_extensions/models/human_pose_estimation/checkpoint_iter_370000.pth --output reflection-evaluation/pose-estimation/
	sudo nvidia-docker build -t nvidia-cuda-test .

run:
	sudo nvidia-docker run -it --expose 5000 --network="host" --privileged --volume=/dev:/dev --mount type=bind,source=${CURDIR},target=/reflection nvidia-cuda-test

restart:
	sudo systemctl restart docker

install:
	sudo apt install docker git
