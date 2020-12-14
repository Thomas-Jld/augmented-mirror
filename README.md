# Augmented mirror

## Description

This project uses multiples recognition softwares to project images 
on a mirror matching the viewpoint of the person standing in front of
it.

## Requirements

- Nvidia-Docker
- Node.js
- A nvidia GPU with drivers installed

## Using the Docker container

To build the container from the docker file, simply use `make build`.<br/>
To execute the container, use `make run`. Make sure that you've already 
installed nvidia-docker and that your computer supports cuda. <br/> 
Inside the docker container execute `launch.sh` to launch the recognition software.

### Manualy launching the intermediate Server
In the server folder, use:
```
node server.js
```
Make sure to be in a docker container if your computer doesn't have node.

### Manualy sending position data to the server
In reflections, while being in a docker container, use:
```
python3 send_data_2.py
```
## Openning the app

Open `client/index.html` with chrome to see result.

## Ressources:
Projects : 
- https://github.com/Daniil-Osokin/lightweight-human-pose-estimation.pytorch
- https://google.github.io/mediapipe/solutions/hands.html
- https://github.com/facebookresearch/detectron2/tree/master/projects/DensePose

Libraries:
- https://github.com/IntelRealSense/librealsense/
- https://github.com/socketio/socket.io
