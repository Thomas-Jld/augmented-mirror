import socketio
import threading
import time
import numpy as np

import torch
import torch.nn as nn
import cv2 as cv

sio = socketio.Client(engineio_logger=True)

def add_data(name, data):
    global AVAILABLE
    if not AVAILABLE:
        while not AVAILABLE:
            time.sleep(NAP)
    else:
        AVAILABLE = False

    DATA[name] = data

    AVAILABLE = True


class IntelVideoReader(object):
    def __init__(self):
        import pyrealsense2 as rs
        
        self.pipe = rs.pipeline()
        config = rs.config()

        self.width = 1280
        self.height = 720

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

        color_frame = np.fliplr(np.asanyarray(color_frame.get_data()))
        depth_frame = np.fliplr(np.asanyarray(depth_frame.get_data()))

        return [color_frame, depth_frame]
        

class CameraVideoReader:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.cap = cv.VideoCapture(0)
        self.cap.set(3,self.width)
        self.cap.set(4,self.height)

    def next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return [frame, None]
        else:
            return [None, None]


class FrameProvider(threading.Thread):
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
            time.sleep(1/(2*FPS))


class BodyProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_body_pose as gbp

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed

    def run(self):
        import get_body_pose as gbp
        print(
        """
        -------------------------------------
        Body pose running
        -------------------------------------
        """)
        while 1:
            start_t = time.time()
            self.pose = gbp.init()

            if color is not None and depth is not None:
                self.data = gbp.find_body_pose(self.pose, color)

                add_data("body_pose", self.data)

            end_t = time.time()
            dt = 1/FPS - (end_t - start_t) if (end_t - start_t) < 1/FPS else 0.01
            time.sleep(dt)


class BodyMeshProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_body_mesh as gm
        threading.Thread.__init__(self)
        self.threadID = threadID
        gm.init_densepose()

    def run(self):
        import get_body_mesh as gm
        print(
        """
        -------------------------------------
        Mesh provider running
        -------------------------------------
        """)

        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gm.infere_on_image(color)

                add_data("body_mesh", self.data)

            end_t = time.time()
            dt = 1/FPS - (end_t - start_t) if (end_t - start_t) < 1/FPS else 0.01
            time.sleep(dt)


class HandsProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_hand_gesture as gh

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.hands = gh.init()

    def run(self):
        import get_hand_gesture as gh
        print(
        """
        -------------------------------------
        Hands provider running
        -------------------------------------
        """)
        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gh.find_hand_pose(self.hands, color)
                add_data("hands_pose", self.data)
            
            end_t = time.time()
            dt = 1/FPS - (end_t - start_t) if (end_t - start_t) < 1/FPS else 0.01
            time.sleep(dt)


class FaceProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_face_mesh as gf

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.faces = gf.init()

    def run(self):
        import get_face_mesh as gf
        print(
        """
        -------------------------------------
        Face mesh running
        -------------------------------------
        """)
        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gf.find_face_mesh(self.faces, color)
                
                add_data("face_mesh", self.data)
            
            end_t = time.time()
            dt = 1/FPS - (end_t - start_t) if (end_t - start_t) < 1/FPS else 0.01
            time.sleep(dt)


class MultipleProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_holistic as gh

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.holistic = gh.init()

    def run(self):
        import get_holistic as gh
        from get_reflection import project
        print(
        """
        -------------------------------------
        Holistic running
        -------------------------------------
        """)
        while 1:
            global PAUSED
            if not PAUSED:
                start_t = time.time()

                if color is not None and depth is not None:
                    self.data = gh.find_all_poses(self.holistic, color)
                    global CHANGED

                    if bool(self.data["body_pose"]):
                        CHANGED = True
                        eyes = self.data["body_pose"][0][2:4]

                        body = project(self.data["body_pose"], eyes, self.feed, depth, 4)
                        add_data("body_pose", body)
                        add_data("right_hand_pose", project(self.data["right_hand_pose"], eyes, self.feed, depth, 2, body[19][-1]))
                        add_data("left_hand_pose", project(self.data["left_hand_pose"], eyes, self.feed, depth, 2, body[20][-1]))
                        add_data("face_mesh", project(self.data["face_mesh"], eyes, self.feed, depth, 2, body[2][-1]))
                
                end_t = time.time()
                dt = 1/FPS - (end_t - start_t) if (end_t - start_t) < 1/FPS else 0.01
                time.sleep(dt)
            else:
                time.sleep(5)


class SendData(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID


    def run(self):
        print(
        """
        -------------------------------------
        Data sender running
        -------------------------------------
        """)
        while 1:
            global PAUSED
            if not PAUSED:
                start_t = time.time()

                global CHANGED
                if CHANGED:
                    global AVAILABLE
                    if not AVAILABLE:
                        while not AVAILABLE:
                            time.sleep(NAP)
                    else:
                        AVAILABLE = False

                    sio.emit("global_data", DATA)
                    AVAILABLE = True
                    CHANGED = False
                end_t = time.time()
                dt = 2/FPS - (end_t - start_t) if (end_t - start_t) < 1/(2*FPS) else 0.01
                time.sleep(dt)
            else:
                time.sleep(5)


@sio.on('pause')
def pause(data: bool):
    global PAUSED
    PAUSED = data


@sio.event
def connect():
    print(
    """
    -------------------------------------
    Connected to the server
    -------------------------------------
    """)

    functionalities = [
        False, # Body pose, requires Face mesh
        False, # Body mesh, requires Body pose
        False, # Hands, requires Body pose
        False, # Face mesh
        True, # Holistic, Body face and hands in one
    ]

    # feed = CameraVideoReader()
    feed = IntelVideoReader()
    Thread1 = FrameProvider("frame", feed)
    
    if functionalities[0]:
        Thread2 = BodyProvider("body_pose", feed)
    if functionalities[1]:
        Thread3 = BodyMeshProvider("body_mesh", feed)
    if functionalities[2]:
        Thread4 = HandsProvider("hands_pose", feed)
    if functionalities[3]:
        Thread5 = FaceProvider("face_mesh", feed)
    if functionalities[4]:
        Thread6 = MultipleProvider("multiple_poses", feed)
        
    print(
    """
    -------------------------------------
    Data initialized, Starting threads
    -------------------------------------
    """)

    Thread1.start()
    if functionalities[0]:
        Thread2.start()
    if functionalities[1]:
        Thread3.start()
    if functionalities[2]:
        Thread4.start()
    if functionalities[3]:
        Thread5.start()
    if functionalities[4]:
        Thread6.start()

    Messenger = SendData("server")
    Messenger.start()


if __name__ == '__main__':
    color = None
    depth = None
    DATA = {
        "face_mesh": [],
        "body_pose": [],
        "left_hand_pose": [],
        "right_hand_pose": [],
        "eyes": [],
    }
    eyes = []
    threads = []

    FPS = 30
    NAP = 0.01

    PROJECT = True
    AVAILABLE = True
    CHANGED = True
    PAUSED = False
    
    sio.connect('http://0.0.0.0:5000')