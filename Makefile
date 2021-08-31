USER=thomasj27
REPO=mirror_release_7
IMNAME = ${USER}/${REPO}

delete:
	sudo nvidia-docker image rm -f $(IMNAME)

clear:
	sudo nvidia-docker rm $(REPO)

build:
	sudo nvidia-docker build -t $(IMNAME) .

push:
	docker push ${IM_NAME}

run:
	-sudo nvidia-docker rm $(REPO)
	sudo nvidia-docker run -d --expose 5000 --network="host" --privileged --volume=/dev:/dev --name=$(REPO) $(IMNAME)

launch:
	-sudo nvidia-docker rm $(REPO)
	sudo nvidia-docker run --expose 5000 --network="host" --privileged --volume=/dev:/dev --name=$(REPO) $(IMNAME)

restart:
	sudo systemctl restart docker

stop:
	sudo docker stop -t 0 $(REPO)
	sleep 1

open:
	DISPLAY=:0 chromium http://127.0.0.1:8000 --start-fullscreen --disk-cache-dir=/dev/null --disk-cache-size=1 --media-cache-size=1 --incognito

server:
	python3 -m http.server -d app/

logs:
	sudo docker logs --follow $(REPO)
