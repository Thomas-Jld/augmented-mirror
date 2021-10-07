# Augmented mirror

## Description

This project uses multiples recognition softwares to project the body
pose and features of the user on a mirror matching his viewpoint.

## Requirements

- Nvidia-Docker
- A nvidia GPU with drivers installed

## Using the Docker container

To build the container from the docker file, simply use `make build`.<br/>
To execute the container, use `make run`. Make sure that you've already
installed nvidia-docker, that your computer supports cuda and that you have exposed your screen on the local network
using `sudo xhost +local:root`.
<br/>
Inside the docker container `launch_reflection.sh` will be executed and launch the recognition software.

### Manualy launching the intermediate Server

In /server, use:

```bash
node server.js
```

Make sure to be in a docker container if your computer doesn't have nodeJS.

### Manualy sending position data to the server

In /reflections, while being in the docker container, use:

```bash
python3 send_data.py
```

## Openning the app

Use `make open` to see the result on the current machine or `make open_ssh` in a ssh connection in a distant machine.

## Ressources:

### Projects :
- https://github.com/openpifpaf/openpifpaf
- https://github.com/Daniil-Osokin/lightweight-human-pose-estimation.pytorch
- https://google.github.io/mediapipe/solutions/hands.html
- https://google.github.io/mediapipe/solutions/holistic.html
- https://github.com/facebookresearch/detectron2/tree/master/projects/DensePose

### Libraries:
- https://github.com/IntelRealSense/librealsense/
- https://github.com/socketio/socket.io
- https://p5js.org/
