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
installed nvidia-docker and that your computer supports cuda. <br/> 
Inside the docker container `launch_reflection.sh` will be executed and launch the recognition software.

### Manualy launching the intermediate Server
In /server, use:
```
node server.js
```
Make sure to be in a docker container if your computer doesn't have nodeJS.

### Manualy sending position data to the server
In /reflections, while being in the docker container, use:
```
python3 send_data.py
```
## Openning the app

Use `make open` to see the result.

## Ressources:

### Projects : 
- https://github.com/Daniil-Osokin/lightweight-human-pose-estimation.pytorch
- https://google.github.io/mediapipe/solutions/hands.html
- https://google.github.io/mediapipe/solutions/holistic.html
- https://github.com/facebookresearch/detectron2/tree/master/projects/DensePose

### Libraries:
- https://github.com/IntelRealSense/librealsense/
- https://github.com/socketio/socket.io
- https://p5js.org/
