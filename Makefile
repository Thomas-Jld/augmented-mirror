delete:
	sudo nvidia-docker image rm -f mirror

clear:
	sudo nvidia-docker container prune

build:
	git clone https://github.com/Thomas-Jld/detectron2 reflection/detectron2
	curl https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl --output reflection/models/model_final_162be9.pkl
	curl https://download.01.org/opencv/openvino_training_extensions/models/human_pose_estimation/checkpoint_iter_370000.pth --output reflection/pose-estimation/checkpoint_iter_370000.pth
	sudo nvidia-docker build -t mirror .

run:
	sudo nvidia-docker run -it --expose 5000 --network="host" --privileged --volume=/dev:/dev --mount type=bind,source=${CURDIR},target=/Miroir mirror

restart:
	sudo systemctl restart docker

install:
	sudo apt install docker git
