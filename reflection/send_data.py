import threading
import time
from queue import Queue
from typing import List

import eventlet
import numpy as np
import socketio


sio = socketio.Server(logger=False, cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

color = None
depth = None

data_queue = Queue(1)
global_data = {
    "face_mesh": [],
    "body_pose": [],
    "left_hand_pose": [],
    "left_hand_sign": [],  #[SIGN, probability]
    "right_hand_pose": [],
    "right_hand_sign": [], #[SIGN, probability]
    "eyes": [],
}
eyes = []
threads = []
client = ""

FPS = 45

PAUSED = False

WIDTH = 640
HEIGHT = 480
WINDOW = 0.5 # Reduce to focus on the middle


"""
* Normalize the data to fit the hand sign inout data
"""
def normalize_data(data: List[List]) -> List[List]:
    return [[x/WIDTH, y/HEIGHT] for _, _, x, y in data]


"""
(Thread)
* Reads frames from the intel Realsense D435I Camera (color and depth frames)
"""
class IntelVideoReader(object):
    def __init__(self):
        import pyrealsense2 as rs

        self.pipe = rs.pipeline()
        config = rs.config()

        self.width = WIDTH
        self.height = HEIGHT

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
        socketisocketioo


"""
(Thread)
* A class that reads frames from the webcam (color only)
"""
class CameraVideoReader:
    def __init__(self):
        import cv2 as cv
        self.width = WIDTH
        self.height = HEIGHT
        self.cap = cv.VideoCapture(0)
        self.cap.set(3,self.width)
        self.cap.set(4,self.height)

    def next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return [frame, None]
        else:
            return [None, None]


"""
(Thread)
* Reads frames using the 2 previous classes' functions
* and stores them into global variables. (global) depth will be none if
* the camera isn't the Intel D435
"""
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
        global color
        global depth
        while 1:
            color, depth = self.feed.next_frame() #Updates global variales
            time.sleep(1/(2*FPS)) # Runs faster to be sure to get the current frame


"""
(Thread)
* Gets body pose from lightweight pose estimation
"""
class BodyProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_body_pose as gbp

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed

    def run(self):
        import get_body_pose as gbp  # Import the code from another python file if the cwd
        print(
        """
        -------------------------------------
        Body pose running
        -------------------------------------
        """)
        self.pose = gbp.init()

        global global_data
        while 1:
            start_t = time.time() # Used to mesure the elapsed time of each loop

            if color is not None and depth is not None:
                self.data = gbp.find_body_pose(self.pose, color, WINDOW) # Infer on image, return keypoints

                global_data["body_pose"] = self.data

                if not data_queue.empty():
                    data_queue.get()
                data_queue.put(global_data)

            end_t = time.time()
            dt = max(1/FPS - (end_t - start_t), 0.001)
            time.sleep(dt) # Sleeps for 1/FPS (e.g: 33ms if FPS=60) if the code is fast enough, else 1 ms


"""
(Thread)
* Gets body mesh from detectron2 (densepose)
! Lib installation steps commented in Docker
"""
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

        global global_data
        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gm.infere_on_image(color)

                global_data["body_mesh"] = self.data

                if not data_queue.empty():
                    data_queue.get()
                data_queue.put(global_data)

            end_t = time.time()
            dt = max(1/FPS - (end_t - start_t), 0.001)
            time.sleep(dt)


"""
(Thread)
* Hands from mediapipe
! Only one instance from mediapipe can run
"""
class HandsProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_hand_gesture as gh
        import get_hand_sign as ghs

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.hands = gh.init()
        self.sign_provider = ghs.init()

    def run(self):
        import get_hand_gesture as gh
        import get_hand_sign as ghs
        print(
        """
        -------------------------------------
        Hands provider running
        -------------------------------------
        """)

        global global_data
        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gh.find_hand_pose(self.hands, color, WINDOW)

                if bool(self.data):
                    global_data["right_hand_pose"] = self.data[0] #Arbitrary, for testing purposes
                    global_data["right_hand_sign"] = ghs.find_gesture(
                        self.sign_provider,
                        normalize_data(self.data[0])
                    )

                    if not data_queue.empty():
                        data_queue.get()
                    data_queue.put(global_data)
            end_t = time.time()
            dt = max(1/FPS - (end_t - start_t), 0.001)
            time.sleep(dt)


"""
(Thread)
* Face from mediapipe
! Only one instance from mediapipe can run
"""
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

        global global_data
        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gf.find_face_mesh(self.faces, color, WINDOW)

                global_data["face_mesh"] = self.data

                if not data_queue.empty():
                    data_queue.get()
                data_queue.put(global_data)

            end_t = time.time()
            dt = max(1/FPS - (end_t - start_t), 0.001)
            time.sleep(dt)


"""
(Thread)
* Body pose from mediapipe
! Only one instance from mediapipe can run
"""
class HolisticProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_holistic as gh
        import get_hand_sign as ghs

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.holistic = gh.init()
        self.sign_provider = ghs.init()

    def run(self):
        import get_holistic as gh
        #* Home made hand signs : https://github.com/Thomas-Jld/gesture-recognition
        import get_hand_sign as ghs
        from get_reflection import project
        print(
        """
        -------------------------------------
        Holistic running
        -------------------------------------
        """)

        global global_data
        while 1:
            if not PAUSED:
                start_t = time.time()

                if color is not None and depth is not None:
                    self.data = gh.find_all_poses(self.holistic, color, WINDOW)

                    if bool(self.data["body_pose"]):
                        eyes = self.data["body_pose"][0][2:4]

                        body = project(self.data["body_pose"], eyes, self.feed, depth, 4)
                        global_data["body_pose"] = body

                        global_data["right_hand_pose"] = project(
                                self.data["right_hand_pose"],
                                eyes,
                                self.feed,
                                depth, 2,
                                body[15][-1]
                            )

                        if len(self.data["right_hand_pose"]) > 0:
                            global_data["right_hand_sign"] = ghs.find_gesture(
                                    self.sign_provider,
                                    normalize_data(self.data["right_hand_pose"])
                                )

                        global_data["left_hand_pose"] = project(
                                self.data["left_hand_pose"],
                                eyes,
                                self.feed,
                                depth,
                                2,
                                body[16][-1]
                            )

                        if len(self.data["left_hand_pose"]) > 0:
                            global_data["left_hand_sign"] = ghs.find_gesture(
                                    self.sign_provider,
                                    normalize_data(self.data["left_hand_pose"])
                                )

                        global_data["face_mesh"] = project(
                                self.data["face_mesh"],
                                eyes,
                                self.feed,
                                depth,
                                2,
                                body[2][-1]
                            )

                        if not data_queue.empty():
                            data_queue.get()
                        data_queue.put(global_data)

                end_t = time.time()
                # print(f"Infer time: {(end_t - start_t)*1000}ms")
                dt = max(1/FPS - (end_t - start_t), 0.001)
                time.sleep(dt)
            else:
                time.sleep(5)


"""
(Thread)
* Body pose from pifpaf
TODO: Select the person
"""
class PifpafProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_pifpaf as gpp
        #* Home made hand signs : https://github.com/Thomas-Jld/gesture-recognition
        import get_hand_sign as ghs

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.processor = gpp.init()
        self.sign_provider = ghs.init()

    def run(self):
        import get_pifpaf as gpp
        import get_hand_sign as ghs
        from get_reflection import project
        print(
        """
        -------------------------------------
        Pifpaf running
        -------------------------------------
        """)

        global global_data
        while 1:
            if not PAUSED:
                start_t = time.time()
                if color is not None and depth is not None:
                    self.data = gpp.find_all_poses(self.processor, color, WINDOW)

                    if bool(self.data["body_pose"]):
                        eyes = self.data["body_pose"][0][2:4]

                        body = project(self.data["body_pose"], eyes, self.feed, depth, 4)
                        global_data["body_pose"] = body

                        global_data["right_hand_pose"] = project(
                                self.data["right_hand_pose"], # Data to project
                                eyes,                         # POV for reflection
                                self.feed,                    # Data from the camera
                                depth,                        # Depth map
                                2,                            # Size of the are to sample from
                                body[9][-1]                   # (Optionnal) Distance to use instead of the real one
                            )

                        if len(self.data["right_hand_pose"]) > 0:
                            global_data["right_hand_sign"] = ghs.find_gesture(
                                    self.sign_provider,
                                    normalize_data(self.data["right_hand_pose"])
                                )

                        global_data["left_hand_pose"] = project(
                                self.data["left_hand_pose"],
                                eyes,
                                self.feed,
                                depth,
                                2,
                                body[10][-1]
                            )

                        if len(self.data["left_hand_pose"]) > 0:
                            global_data["left_hand_sign"] = ghs.find_gesture(
                                    self.sign_provider,
                                    normalize_data(self.data["left_hand_pose"])
                                )

                        global_data["face_mesh"] = project(
                                self.data["face_mesh"],
                                eyes,
                                self.feed,
                                depth,
                                2,
                                body[0][-1]
                            )

                        if not data_queue.empty():
                            data_queue.get()
                        data_queue.put(global_data)

                time.sleep(max(1/FPS - (time.time() - start_t), 0.001))
            else:
                time.sleep(5)


"""
* Sends data to the client
"""
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
            if not PAUSED:
                start_t = time.time()
                data = data_queue.get()
                sio.emit("update", data)
                end_t = time.time()
                dt = max(1/FPS - (end_t - start_t), 0)
                time.sleep(dt)
            else:
                time.sleep(5)

@sio.on('pause')
def pause(data: bool):
    global PAUSED
    PAUSED = data


@sio.event
def connect(sid, environ):
    global client
    print('connect ', sid)
    client = sid

"""
* Init everything when starting the program
"""
if __name__ == '__main__':

    functionalities = {
        "body_pose": [False, BodyProvider], # Body pose, requires Face mesh
        "body_mesh": [False, BodyMeshProvider], # Body mesh, requires Body pose
        "hands_pose": [False, HandsProvider], # Hands, requires Body pose
        "face_mesh": [False, FaceProvider], # Face mesh
        "holistic_pose": [True, HolisticProvider], # Holistic, Body face and hands in one
        "pifpaf_pose": [False, PifpafProvider], # Pifpaf, Body face and hands in one
    }

    # feed = CameraVideoReader()
    feed = IntelVideoReader()

    camThread = FrameProvider("frame", feed)

    Threads = []
    for name in functionalities:
        if functionalities[name][0]:
            Threads.append(functionalities[name][1](name, feed))

    print(
    """
    -------------------------------------
    Data initialized, Starting threads
    -------------------------------------
    """)

    camThread.start()
    for thread in Threads:
        thread.start()

    Messenger = SendData("server")
    Messenger.start()

    print(
    """
    -------------------------------------
    Starting server
    -------------------------------------
    """)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
