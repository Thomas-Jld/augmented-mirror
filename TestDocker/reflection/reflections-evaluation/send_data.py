import socketio

from get_reflection import *

sio = socketio.Client(engineio_logger=True)

@sio.event
def connect():
    print('connected to server')
    send_data()


def send_data():
    net = init()
    print("Running")
    while True:
        sio.emit("reflection", find_reflection(net))
    pass

if __name__ == '__main__':
    sio.connect('http://0.0.0.0:5000')
