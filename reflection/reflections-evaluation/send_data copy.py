import socketio
import threading
from time import sleep


import get_reflection as gr
# import get_temperature as gt

sio = socketio.Client(engineio_logger=True)

class video_feed(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    
    def run(self):
        


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
