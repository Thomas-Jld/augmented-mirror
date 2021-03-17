IMNAME = mirror_release_3

delete:
	sudo nvidia-docker image rm -f $(IMNAME)

clear:
	sudo nvidia-docker rm $(IMNAME)

build:
	sudo nvidia-docker build -t $(IMNAME) .

run:
	sudo nvidia-docker run -it --expose 5000 --network="host" --privileged --volume=/dev:/dev $(IMNAME)
	#  --mount type=bind,source=${CURDIR},target=/Miroir

launch:
	-sudo nvidia-docker rm $(IMNAME)
	sudo nvidia-docker run -d --expose 5000 --network="host" --privileged --volume=/dev:/dev --name=$(IMNAME) $(IMNAME)
	
restart:
	sudo systemctl restart docker

stop:
	sudo docker stop -t 0 $(IMNAME)
	sleep 1

open:
	DISPLAY=:0 chromium apps/index.html --start-fullscreen

logs:
	sudo docker logs --follow $(IMNAME)
