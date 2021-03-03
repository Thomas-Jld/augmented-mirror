delete:
	sudo nvidia-docker image rm -f mirror_release_2

clear:
	sudo nvidia-docker container prune

build:
	sudo nvidia-docker build -t mirror_release_2 .

run:
	sudo nvidia-docker run -it --expose 5000 --network="host" --privileged --volume=/dev:/dev mirror_release_2
	#  --mount type=bind,source=${CURDIR},target=/Miroir

launch:
	sudo nvidia-docker run -d --expose 5000 --network="host" --privileged --volume=/dev:/dev --name=mirror_release_2 mirror_release_2
	
restart:
	sudo systemctl restart docker

stop:
	sudo docker stop -t 0 mirror_release_2
	sleep 5

open:
	DISPLAY=:0 chromium apps/index.html --start-fullscreen

logs:
	sudo docker logs mirror_release_2
