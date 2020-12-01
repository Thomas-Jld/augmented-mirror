# Miroir

## Requirements

- Nvidia-Docker
- Node.js
- A nvidia GPU with drivers installed

## Using the Docker container
```
cd reflection/
```
To build the container from the docker file, simply use `make build`.<br/>
To execute the container, use `make run`. Make sure that you've already installed nvidia-docker and that your computer support cuda.

### Launching the intermediate Server
In the server folder, use:
```
node server.js
```

### Sending position data to the server
In reflections-evaluation, use:
```
python3 send_data.py
```
## Launch the app

Open `client/index.html` with chrome to see result.

## Ressources:
Projects : 
- https://github.com/Daniil-Osokin/lightweight-human-pose-estimation.pytorch
- https://google.github.io/mediapipe/solutions/hands.html
- https://github.com/facebookresearch/detectron2/tree/master/projects/DensePose

Libraries:
- https://github.com/IntelRealSense/librealsense/
- https://github.com/socketio/socket.io
