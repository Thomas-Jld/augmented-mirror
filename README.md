# Miroir

## Using the Docker container
```
cd reflection/
```
To build the container from the docker file, simply use `make build`.<br/>
To execute the container, use `make run`. Make sure that you've already installed nvidia-docker and that your computer support cuda.


### Launching the intermediate Server
```
cd reflection/server/
node server.js
```

### Sending position data to the server
```
python3 send-data.py
```
## Launch the app

open reflection/server/index.html with chrome to see result.

## Ressources:
https://github.com/Daniil-Osokin/lightweight-human-pose-estimation.pytorch
https://github.com/IntelRealSense/librealsense/
https://github.com/socketio/socket.io
