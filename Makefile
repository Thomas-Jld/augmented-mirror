delete:
	sudo nvidia-docker image rm -f mirror

clear:
	sudo nvidia-docker container prune

build:
	sudo nvidia-docker build -t mirror .

run:
	sudo nvidia-docker run -it --expose 5000 --network="host" --privileged --volume=/dev:/dev mirror
	#  --mount type=bind,source=${CURDIR},target=/Miroir
	
restart:
	sudo systemctl restart docker

install:
	sudo apt install docker git
