import socketio

from time import sleep


import get_reflection as gr
# import get_temperature as gt

sio = socketio.Client(engineio_logger=True)

@sio.event
def connect():
    print('connected to server')
    send_data()


def send_data():
    net = gr.init()
    print("Running")
    while True:
        data = gr.find_reflection(net)
        if data:
            sio.emit("reflection", data)
        else:
            sleep(0.05)
    pass

if __name__ == '__main__':
    sio.connect('http://0.0.0.0:5000')
