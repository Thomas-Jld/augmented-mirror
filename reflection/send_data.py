import cv2 as cv2

import threading
import time
from queue import Queue
from typing import List

import eventlet
import numpy as np
import socketio


sio = socketio.Server(logger=False, cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

color = None
depth = None

data_queue = Queue(1)
global_data = {
    "face_mesh": [],
    "body_pose": [],
    "left_hand_pose": [],
    "left_hand_sign": [],  # [SIGN, probability]
    "right_hand_pose": [],
    "right_hand_sign": [],  # [SIGN, probability]
    "eyes": [],
}
eyes = []
threads = []
client = ""

FPS = 45

PAUSED = False

WIDTH = 640
HEIGHT = 480

RESOLUTION_X = 1080
RESOLUTION_Y = 1920

DIMENSION_X = 392.85
DIMENSION_Y = 698.4

OFFSET_X = -260
OFFSET_Y = 70

WINDOW = 0.7  # Reduce to focus on the middle
MODE = "DISPLAY"  # "STREAM"


"""
* Normalize the data to fit the hand sign inout data
"""


def normalize_data(data: List[List]) -> List[List]:
    return [[x / WIDTH, y / HEIGHT] for _, _, x, y in data]

def lerp(P1, P2, f):
    return P1 + (P2 - P1) * f


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

        config.enable_stream(
            rs.stream.depth, self.width, self.height, rs.format.z16, 30
        )
        config.enable_stream(
            rs.stream.color, self.width, self.height, rs.format.bgr8, 30
        )

        profile = self.pipe.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        clipping_distance_in_meters = 3
        clipping_distance = clipping_distance_in_meters / self.depth_scale

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.depth_to_disparity = rs.disparity_transform(True)
        self.disparity_to_depth = rs.disparity_transform(False)
        self.dec_filter = rs.decimation_filter()
        self.temp_filter = rs.temporal_filter()
        self.spat_filter = rs.spatial_filter()

    def next_frame(self):
        frameset = self.pipe.wait_for_frames()

        aligned_frames = self.align.process(frameset)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        self.depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        self.color_intrinsics = color_frame.profile.as_video_stream_profile().intrinsics

        depth_frame = self.depth_to_disparity.process(depth_frame)
        depth_frame = self.dec_filter.process(depth_frame)
        depth_frame = self.temp_filter.process(depth_frame)
        depth_frame = self.spat_filter.process(depth_frame)
        depth_frame = self.disparity_to_depth.process(depth_frame)
        depth_frame = depth_frame.as_depth_frame()

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
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

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
        """
        )
        global color
        global depth
        while 1:
            color, depth = self.feed.next_frame()  # Updates global variales
            time.sleep(1 / (2 * FPS))  # Runs faster to be sure to get the current frame


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
        """
        )
        self.pose = gbp.init()

        global global_data
        while 1:
            start_t = time.time()  # Used to mesure the elapsed time of each loop

            if color is not None and depth is not None:
                self.data = gbp.find_body_pose(
                    self.pose, color, WINDOW
                )  # Infer on image, return keypoints

                global_data["body_pose"] = self.data

                if not data_queue.empty():
                    data_queue.get()
                data_queue.put(global_data)

            end_t = time.time()
            dt = max(1 / FPS - (end_t - start_t), 0.001)
            time.sleep(
                dt
            )  # Sleeps for 1/FPS (e.g: 33ms if FPS=60) if the code is fast enough, else 1 ms


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
        """
        )

        global global_data
        while 1:
            start_t = time.time()

            if color is not None:
                self.data = gh.find_hand_pose(self.hands, color, WINDOW)

                if bool(self.data):
                    global_data["right_hand_pose"] = self.data[
                        0
                    ]  # Arbitrary, for testing purposes
                    # global_data["right_hand_sign"] = ghs.find_gesture(
                    #     self.sign_provider,
                    #     normalize_data(self.data[0])
                    # )

                    if not data_queue.empty():
                        data_queue.get()
                    data_queue.put(global_data)
            end_t = time.time()
            dt = max(1 / FPS - (end_t - start_t), 0.001)
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
        """
        )

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
            dt = max(1 / FPS - (end_t - start_t), 0.001)
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

        # * Home made hand signs : https://github.com/Thomas-Jld/gesture-recognition
        import get_hand_sign as ghs
        from get_reflection import project

        print(
            """
        -------------------------------------
        Holistic running
        -------------------------------------
        """
        )

        global global_data
        while 1:
            if not PAUSED:
                start_t = time.time()

                if color is not None and depth is not None:
                    self.data = gh.find_all_poses(self.holistic, color, WINDOW)

                    if bool(self.data["body_pose"]):
                        eyes = self.data["body_pose"][0][2:4]

                        body = project(
                            self.data["body_pose"], eyes, self.feed, depth, 4
                        )
                        global_data["body_pose"] = body

                        global_data["right_hand_pose"] = project(
                            self.data["right_hand_pose"],
                            eyes,
                            self.feed,
                            depth,
                            2,
                            body[15][-1],
                        )

                        if len(self.data["right_hand_pose"]) > 0:
                            global_data["right_hand_sign"] = ghs.find_gesture(
                                self.sign_provider,
                                normalize_data(self.data["right_hand_pose"]),
                            )

                        global_data["left_hand_pose"] = project(
                            self.data["left_hand_pose"],
                            eyes,
                            self.feed,
                            depth,
                            2,
                            body[16][-1],
                        )

                        if len(self.data["left_hand_pose"]) > 0:
                            global_data["left_hand_sign"] = ghs.find_gesture(
                                self.sign_provider,
                                normalize_data(self.data["left_hand_pose"]),
                            )

                        global_data["face_mesh"] = project(
                            self.data["face_mesh"],
                            eyes,
                            self.feed,
                            depth,
                            2,
                            body[2][-1],
                        )

                        if not data_queue.empty():
                            data_queue.get()
                        data_queue.put(global_data)

                end_t = time.time()
                # print(f"Infer time: {(end_t - start_t)*1000}ms")
                dt = max(1 / FPS - (end_t - start_t), 0.001)
                time.sleep(dt)
            else:
                time.sleep(5)



class DrawPose:
    def __init__(self):

        self.body_junctions = [
            [[0, 1], [0, 4], [1, 2], [2, 3], [3, 7], [4, 5], [5, 6], [6, 8]],
            [[9, 10]],
            [
                [11, 12],
                [11, 13],
                [11, 23],
                [12, 14],
                [12, 24],
                [13, 15],
                [14, 16],
                [15, 17],
                [15, 19],
                [15, 21],
                [16, 18],
                [16, 20],
                [16, 22],
                [17, 19],
                [18, 20],
                [23, 24],
                [23, 25],
                [24, 26],
                [25, 27],
                [26, 28],
                [27, 29],
                [27, 31],
                [28, 30],
                [28, 32],
            ],
        ]

        self.keypoints = [
            "nose",
            "left_eye_inner",
            "left_eye",
            "left_eye_outer",
            "right_eye_inner",
            "right_eye",
            "right_eye_outer",
            "left_ear",
            "right_ear",
            "mouth_left",
            "mouth_right",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_pinky",
            "right_pinky",
            "left_index",
            "right_index",
            "left_thumb",
            "right_thumb",
            "left_hip",
            "right_hip",
            "left_knee",
            "left_ankle",
            "right_ankle",
            "left_heel",
            "right_heel",
            "left_foot_index",
            "right_foot_index",
        ]

        self.body_pose = []
        self.body_pose_t = []

        self.color = (0, 255, 0)
        self.thickness = 9

        self.show_head = False
        self.show_wrist = True

    def draw(self, image):
        for i in range(len(self.body_pose)):
            if self.body_pose[2:4] != [-1, -1]:
                if len(self.body_pose_t) == len(self.body_pose):
                    newx = RESOLUTION_X * (self.body_pose[i][2] - OFFSET_X) / DIMENSION_X
                    newy = RESOLUTION_Y * (self.body_pose[i][3] - OFFSET_Y) / DIMENSION_Y
                    if newy > 0:
                        x = lerp(self.body_pose_t[i][0], newx, 0.8)
                        y = lerp(self.body_pose_t[i][1], newy, 0.8)
                    else:
                        x = lerp(self.body_pose_t[i][0], newx, 0.01)
                        y = lerp(self.body_pose_t[i][1], newy, 0.01)

                    self.body_pose_t[i] = [x, y]
                else:
                    x = RESOLUTION_X * (self.body_pose[i][2] - OFFSET_X) / DIMENSION_X
                    y = RESOLUTION_Y * (self.body_pose[i][3] - OFFSET_Y) / DIMENSION_Y
                    self.body_pose_t.append([x, y])

        for parts in self.body_junctions:
            for pair in parts:
                try:
                    if self.body_pose_t[pair[0]][1] > 0 and self.body_pose_t[pair[1]][1] > 0 and (self.show_head or (pair[1] > 10 and pair[0] > 10)): # and (self.show_wrist or ([17, 18, 19, 20] not in pair[0]) and [17, 18, 19, 20, 21, 22].includes(pair[1])))
                        image = cv2.line(image, self.body_pose_t[pair[0]], self.body_pose_t[pair[1]], self.color, self.thickness)
                except:
                    pass
        return image

class DisplayResult:
    def __init__(self):
        self.window_name = "draw"
        self.body = DrawPose()

    def run(self):
        import cv2 as cv2

        while 1:
            image = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
            image = self.body.draw(image)
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(
                self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )
            cv2.imshow(self.window_name, image)
            key = cv2.waitKey(0)
            if key == 27:
                break


"""
(Thread)
* Body pose from pifpaf
TODO: Select the person
"""


class PifpafProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_pifpaf as gpp

        # * Home made hand signs : https://github.com/Thomas-Jld/gesture-recognition
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
        """
        )

        global global_data
        while 1:
            if not PAUSED:
                start_t = time.time()
                if color is not None and depth is not None:
                    self.data = gpp.find_all_poses(self.processor, color, WINDOW)

                    if bool(self.data["body_pose"]):
                        eyes = self.data["body_pose"][0][2:4]

                        body = project(
                            self.data["body_pose"], eyes, self.feed, depth, 4
                        )
                        global_data["body_pose"] = body

                        global_data["right_hand_pose"] = project(
                            self.data["right_hand_pose"],  # Data to project
                            eyes,  # POV for reflection
                            self.feed,  # Data from the camera
                            depth,  # Depth map
                            2,  # Size of the are to sample from
                            body[9][
                                -1
                            ],  # (Optionnal) Distance to use instead of the real one
                        )

                        if len(self.data["right_hand_pose"]) > 0:
                            global_data["right_hand_sign"] = ghs.find_gesture(
                                self.sign_provider,
                                normalize_data(self.data["right_hand_pose"]),
                            )

                        global_data["left_hand_pose"] = project(
                            self.data["left_hand_pose"],
                            eyes,
                            self.feed,
                            depth,
                            2,
                            body[10][-1],
                        )

                        if len(self.data["left_hand_pose"]) > 0:
                            global_data["left_hand_sign"] = ghs.find_gesture(
                                self.sign_provider,
                                normalize_data(self.data["left_hand_pose"]),
                            )

                        global_data["face_mesh"] = project(
                            self.data["face_mesh"],
                            eyes,
                            self.feed,
                            depth,
                            2,
                            body[0][-1],
                        )

                        if not data_queue.empty():
                            data_queue.get()
                        data_queue.put(global_data)

                time.sleep(max(1 / FPS - (time.time() - start_t), 0.001))
            else:
                time.sleep(5)


"""
* Sends data to the client upon request
"""


@sio.on("update")
def update(*args) -> None:
    data = data_queue.get()
    sio.emit("global_data", global_data)


@sio.on("pause")
def pause(data: bool):
    global PAUSED
    PAUSED = data


@sio.event
def connect(sid, environ):
    global client
    print("connect ", sid)
    client = sid


"""
* Init everything when starting the program
"""
if __name__ == "__main__":

    functionalities = {
        "body_pose": [False, BodyProvider],  # Body pose, requires Face mesh
        "hands_pose": [False, HandsProvider],  # Hands, requires Body pose
        "face_mesh": [False, FaceProvider],  # Face mesh
        "holistic_pose": [
            True,
            HolisticProvider,
        ],  # Holistic, Body face and hands in one
        "pifpaf_pose": [False, PifpafProvider],  # Pifpaf, Body face and hands in one
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
    """
    )

    camThread.start()
    for thread in Threads:
        thread.start()

    # Messenger = SendData("server")
    # Messenger.start()

    if MODE == "STREAM":
        print(
            """
        -------------------------------------
        Starting server
        -------------------------------------
        """
        )
        eventlet.wsgi.server(eventlet.listen(("", 5000)), app)
    elif MODE == "DISPLAY":
        display = DisplayResult()
        display.run()
