import socketio
import threading
import time
import numpy as np

import cv2 as cv
import pyrealsense2 as rs


import get_reflection as gr
# import get_temperature as gt
import get_body_mesh as gm
import get_hand_gesture as gh

sio = socketio.Client(engineio_logger=True)

class IntelVideoReader(object):
    def __init__(self):
        self.pipe = rs.pipeline()
        config = rs.config()

        self.width = 640
        self.height = 480

        config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, 30)

        profile = self.pipe.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        clipping_distance_in_meters = 3
        clipping_distance = clipping_distance_in_meters / self.depth_scale

        align_to = rs.stream.color
        self.align = rs.align(align_to)


    def next_frame(self):
        frameset = self.pipe.wait_for_frames()

        aligned_frames = self.align.process(frameset)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        self.depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        self.color_intrinsics = color_frame.profile.as_video_stream_profile().intrinsics

        color_frame = np.asanyarray(color_frame.get_data())
        depth_frame = np.asanyarray(depth_frame.get_data())

        return [color_frame, depth_frame]
        

class CameraVideoReader:
    def __init__(self):
        self.cap = cv.VideoCapture(0)

    def next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return [frame, None]
        else:
            return [None, None]


class frame_provider(threading.Thread):
    def __init__(self, threadID, feed):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed

    def run(self):
        print(
        """
        -------------------------------------
        Frame provider running
        -------------------------------------
        """)
        while 1:
            global color
            global depth
            color, depth = self.feed.next_frame()
            time.sleep(0.01)


class joint_provider(threading.Thread):
    def __init__(self, threadID, feed, net):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.net = net

    def run(self):
        print(
        """
        -------------------------------------
        Joint provider running
        -------------------------------------
        """)
        while 1:
            if color is not None and depth is not None:
                self.data = gr.find_reflection(self.net, color, depth, self.feed)
                if self.data != {}:
                    global ratio
                    ratio = self.data["ratio"]
                    sio.emit("joint", self.data)
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.02)


class mesh_provider(threading.Thread):
    def __init__(self, threadID, feed):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        print(
        """
        -------------------------------------
        Mesh provider running
        -------------------------------------
        """)
        while 1:
            if color is not None:
                print("Frame ok")
                self.data = gm.infere_on_image(color)
                if self.data.all() is not [0, 0, 0]:
                    print("Sending mesh")
                    sio.emit("mesh", self.data.tolist())
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.02)


class hands_provider(threading.Thread):
    def __init__(self, threadID, feed, hands):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.hands = hands

    def run(self):
        print(
        """
        -------------------------------------
        Hands provider running
        -------------------------------------
        """)
        while 1:
            if color is not None:
                self.data = gh.find_hand_pose(self.hands, color)
                if self.data is not None and self.data != []:
                    self.data.append(ratio)
                    sio.emit("hands", self.data)
                    time.sleep(0.01)
                else:
                    time.sleep(0.001)
            else:
                time.sleep(0.02)




@sio.event
def connect():
    functionalities = [
        False, # Joint
        False, # Body mesh, requires Joint
        True, # Hands, requires Joint
    ]
    print(
    """
    -------------------------------------
    Connected to the server
    -------------------------------------
    """)
    net = gr.init()
    gm.init_densepose()
    hands = gh.init()

    print(
    """
    -------------------------------------
    Data initialized
    -------------------------------------
    """)

    feed = CameraVideoReader()

    Thread1 = frame_provider("frame", feed)
    if functionalities[0]:
        Thread2 = joint_provider("joint", feed, net)
    if functionalities[1]:
        Thread3 = mesh_provider("mesh", feed)
    if functionalities[2]:
        Thread4 = hands_provider("hands", feed, hands)
        

    print(
    """
    -------------------------------------
    Starting threads 
    -------------------------------------
    """)

    Thread1.start()
    if functionalities[0]:
        Thread2.start()
    if functionalities[1]:
        Thread3.start()
    if functionalities[2]:
        Thread4.start()



if __name__ == '__main__':
    color = None
    depth = None
    ratio = [1, 1]
    threads = []
    sio.connect('http://0.0.0.0:5000')
