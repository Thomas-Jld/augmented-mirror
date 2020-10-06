sudo docker run -it --device=/dev/video2 test1
sudo docker run --privileged --volume=/dev:/dev -it test1
