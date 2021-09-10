# Augmented mirror

## Description

This project uses multiples recognition softwares to project the body 
pose and features of the user on a mirror matching his viewpoint.

## Requirements

- Nvidia-Docker
- A nvidia GPU with drivers installed
- Chromium web browser

## Using the Docker container

To build the container from the docker file, simply use `make build`.<br/>
To execute the container, use `make run`. Make sure that you've already 
installed nvidia-docker and that your computer supports cuda. <br/> 
Inside the docker container `launch_reflection.sh` will be executed and launch the recognition software.

### (Optional) Manualy sending position data to the server

In /reflections, while being in the docker container, use:

```bash
python3 send_data.py
```

## Openning the app

You have to use a simple local http server to host the index.html and all the files. For exemple, use `python3 -m http.server` in the apps/ folder.

Use `make open` to see the result.

## Ressources:

- https://github.com/openpifpaf/openpifpaf
- https://google.github.io/mediapipe/solutions/holistic.html
- https://google.github.io/mediapipe/solutions/hands.html
- https://github.com/IntelRealSense/librealsense/
- https://github.com/socketio/socket.io
- https://p5js.org/
