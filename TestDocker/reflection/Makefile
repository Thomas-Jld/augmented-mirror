delete:
	sudo nvidia-docker image rm -f nvidia-cuda-test

clear:
	sudo nvidia-docker container prune

build:
	sudo nvidia-docker build -t nvidia-cuda-test .

run:
	sudo nvidia-docker run -it --expose 5000 --privileged --volume=/dev:/dev --mount type=bind,source=${CURDIR},target=/reflection nvidia-cuda-test

restart:
	sudo systemctl restart docker

install:
	sudo apt install docker git
