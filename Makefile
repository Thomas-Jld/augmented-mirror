IMNAME = mirror_demo_6

delete:
	sudo nvidia-docker image rm -f $(IMNAME)

clear:
	sudo nvidia-docker rm $(IMNAME)

build:
	sudo nvidia-docker build -t $(IMNAME) .

run:
	-sudo nvidia-docker rm $(IMNAME)
	sudo nvidia-docker run -d --expose 5000 --network="host" --privileged --volume=/dev:/dev --name=$(IMNAME) $(IMNAME)

launch:
	-echo -n "0000:00:14.0" | tee /sys/bus/pci/drivers/xhci_hcd/unbind
	-echo -n "0000:00:14.0" | tee /sys/bus/pci/drivers/xhci_hcd/bind
	-sudo nvidia-docker rm $(IMNAME)
	sudo nvidia-docker run --expose 5000 --network="host" --privileged --volume=/dev:/dev --name=$(IMNAME) $(IMNAME)
	
restart:
	sudo systemctl restart docker

stop:
	sudo docker stop -t 0 $(IMNAME)
	sleep 1

open:
	DISPLAY=:0 chromium http://127.0.0.1:8000 --start-fullscreen --disk-cache-dir=/dev/null --disk-cache-size=1 --media-cache-size=1

server:
	python3 -m http.server -d app/

logs:
	sudo docker logs --follow $(IMNAME)