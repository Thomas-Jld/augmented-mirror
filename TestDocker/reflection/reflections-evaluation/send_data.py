import socketio
# 
# from get_reflection import *

sio = socketio.Client(engineio_logger=True)

@sio.event
def connect():
    print('connected to server')
    while True:
        pass


def send_data():
    # net = init()
    # print("Running")
    # while True:
    #     print(find_reflection(net))
    pass

if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    send_data()
