import threading
import time
from queue import Queue
from typing import List

import cv2 as cv
import eventlet
import numpy as np
import socketio
from cv2 import cv2

from utils import BODY_KEYPOINTS, BODY_LINKS

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

client = ""

FPS = 45

PAUSED = False

WIDTH = 640  # Camera image shape
HEIGHT = 480

RESOLUTION_X = 1080  # Screen resolution in pixel
RESOLUTION_Y = 1920

DIMENSION_X = 392.85  # Screen dimensions in mm
DIMENSION_Y = 698.4

OFFSET_X = -260  # Camera offset from screen
OFFSET_Y = 70

WINDOW = 0.7  # Reduce to focus on the middle
MODE = "STREAM"  # "STREAM" or "DISPLAY"

DEBUG_TIME = False
DEBUG_DATA = False


def normalize_data(data: List[List]) -> List[List]:
    """Normalize the data to fit the hand sign inout data"""
    return [[x / WIDTH, y / HEIGHT] for x, y in data]


def lerp(P1, P2, f):
    """Simple Linear Interpolation of two values"""
    return P1 + (P2 - P1) * f


class IntelVideoReader:
    """
    (Thread)
    * Reads frames from the intel Realsense D435I Camera (color and depth frames)
    """

    def __init__(self):
        import pyrealsense2 as rs

        self.pipe = rs.pipeline()
        config = rs.config()

        # ctx = rs.context()
        # devices = ctx.query_devices()
        # for dev in devices:
        #     dev.hardware_reset()

        self.width = WIDTH
        self.height = HEIGHT

        config.enable_stream(
            rs.stream.depth, self.width, self.height, rs.format.z16, 60
        )
        config.enable_stream(
            rs.stream.color, self.width, self.height, rs.format.bgr8, 60
        )

        profile = self.pipe.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        clipping_distance_in_meters = 3
        clipping_distance = clipping_distance_in_meters / self.depth_scale

        # device = profile.get_device()
        # depth_sensor = device.first_depth_sensor()
        # device.hardware_reset()

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.depth_to_disparity = rs.disparity_transform(True)
        self.disparity_to_depth = rs.disparity_transform(False)
        self.dec_filter = rs.decimation_filter()
        self.temp_filter = rs.temporal_filter()
        self.spat_filter = rs.spatial_filter()

    def next_frame(self):
        """Collects color and frames"""
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


class CameraVideoReader:
    """
    (Thread)
    * A class that reads frames from the webcam (color only)
    """

    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.cap = cv.VideoCapture(0)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

    def next_frame(self):
        """Collects color frames"""

        _, frame = self.cap.read()
        return [frame, None]


class FrameProvider(threading.Thread):
    """
    (Thread)
    * Reads frames using the 2 previous classes' functions
    * and stores them into global variables. (global) depth will be none if
    * the camera isn't the Intel D435
    """

    def __init__(self, threadID, feed):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed

    def run(self):
        """Update frames"""
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


class BodyProvider(threading.Thread):
    """
    (Thread)
    * Gets body pose from lightweight pose estimation
    """

    def __init__(self, threadID, feed):
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
        pose = gbp.init()

        while 1:
            start_t = time.time()  # Used to mesure the elapsed time of each loop

            if color is not None and depth is not None:
                data = gbp.find_body_pose(
                    pose, color, WINDOW
                )  # Infer on image, return keypoints

                global_data["body_pose"] = data

                if not data_queue.empty():
                    data_queue.get()
                data_queue.put(global_data)

            end_t = time.time()
            dt = max(1 / FPS - (end_t - start_t), 0.001)
            time.sleep(
                dt
            )  # Sleeps for 1/FPS (e.g: 33ms if FPS=60) if the code is fast enough, else 1 ms


class HandsProvider(threading.Thread):
    """
    (Thread)
    * Hands from mediapipe
    ! Only one instance from mediapipe can run
    """

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

        # import get_hand_sign as ghs

        print(
            """
        -------------------------------------
        Hands provider running
        -------------------------------------
        """
        )

        while 1:
            start_t = time.time()

            if color is not None:
                data = gh.find_hand_pose(self.hands, color, WINDOW)

                if bool(data):
                    global_data["right_hand_pose"] = data[
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


class FaceProvider(threading.Thread):
    """
    (Thread)
    * Face from mediapipe
    ! Only one instance from mediapipe can run
    """

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

        while 1:
            start_t = time.time()

            if color is not None:
                data = gf.find_face_mesh(self.faces, color, WINDOW)

                global_data["face_mesh"] = data

                if not data_queue.empty():
                    data_queue.get()
                data_queue.put(global_data)

            end_t = time.time()
            dt = max(1 / FPS - (end_t - start_t), 0.001)
            time.sleep(dt)


class HolisticProvider(threading.Thread):
    """
    (Thread)
    * Body pose from mediapipe
    ! Only one instance from mediapipe can run
    """

    def __init__(self, threadID, feed):
        import get_hand_sign as ghs
        import get_holistic as gh

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.holistic = gh.init()
        self.sign_provider = ghs.init()

    def run(self):
        # * Home made hand signs : https://github.com/Thomas-Jld/gesture-recognition
        import get_hand_sign as ghs
        import get_holistic as gh
        from get_reflection import project

        print(
            """
        -------------------------------------
        Holistic running
        -------------------------------------
        """
        )

        while 1:
            if not PAUSED:
                start_t = time.time()

                if color is not None and depth is not None:
                    # print(f'color: ' + :color)
                    data = gh.find_all_poses(self.holistic, color, WINDOW)
                    if DEBUG_DATA:
                        print(data)

                    if bool(data["body_pose"]):
                        if DEBUG_TIME:
                            flag_1 = time.time()
                            print(f"Inference: {(flag_1 - start_t)*1000} ms")
                        eyes = data["body_pose"][0]

                        body = project(
                            points=data["body_pose"],
                            eyes_position=eyes,
                            video_provider=self.feed,
                            depth_frame=depth,
                            depth_radius=4,
                        )
                        global_data["body_pose"] = body

                        global_data["right_hand_pose"] = project(
                            points=data["right_hand_pose"],
                            eyes_position=eyes,
                            video_provider=self.feed,
                            depth_frame=depth,
                            depth_radius=2,
                            ref=body[15][-1],
                        )

                        if len(data["right_hand_pose"]) > 0:
                            global_data["right_hand_sign"] = ghs.find_gesture(
                                self.sign_provider,
                                normalize_data(data["right_hand_pose"]),
                            )

                        global_data["left_hand_pose"] = project(
                            points=data["left_hand_pose"],
                            eyes_position=eyes,
                            video_provider=self.feed,
                            depth_frame=depth,
                            depth_radius=2,
                            ref=body[16][-1],
                        )

                        if len(data["left_hand_pose"]) > 0:
                            global_data["left_hand_sign"] = ghs.find_gesture(
                                self.sign_provider,
                                normalize_data(data["left_hand_pose"]),
                            )

                        global_data["face_mesh"] = project(
                            points=data["face_mesh"],
                            eyes_position=eyes,
                            video_provider=self.feed,
                            depth_frame=depth,
                            depth_radius=2,
                            ref=body[2][-1],
                        )

                        if DEBUG_TIME:
                            flag_2 = time.time()
                            print(f"Projection: {(flag_2 - flag_1)*1000} ms")

                        if not data_queue.empty():
                            data_queue.get()
                        data_queue.put(global_data)

                        if DEBUG_TIME:
                            print(f"Adding to queue: {(time.time() - flag_2)*1000} ms")

                end_t = time.time()

                if DEBUG_TIME:
                    print(f"Infer time: {(end_t - start_t)*1000}ms")
                    print(f"FPS: {int(1/(end_t - start_t))}")

                dt = max(1 / FPS - (end_t - start_t), 0.001)
                time.sleep(dt)
            else:
                time.sleep(5)


class DrawPose:
    """Use Body parametters to draw the body on a provided image"""

    def __init__(self):

        self.body_junctions = BODY_LINKS

        self.keypoints = BODY_KEYPOINTS

        self.body_pose = []
        self.body_pose_t = []

        self.color = (255, 255, 255)
        self.thickness = 5

        self.show_head = False
        self.show_wrist = True

    def draw(self, image, data):
        """Draws the body on an opencv image"""

        self.body_pose = data["body_pose"]

        if len(self.body_pose) == 0:
            return image

        for i, pose in enumerate(self.body_pose):
            if self.body_pose[2:4] != [-1, -1]:
                if len(self.body_pose_t) == len(self.body_pose):
                    newx = RESOLUTION_X * (pose[0] - OFFSET_X) / DIMENSION_X
                    newy = RESOLUTION_Y * (pose[1] - OFFSET_Y) / DIMENSION_Y
                    if newy > 0:
                        x = lerp(self.body_pose_t[i][0], newx, 0.8)
                        y = lerp(self.body_pose_t[i][1], newy, 0.8)
                    else:
                        x = lerp(self.body_pose_t[i][0], newx, 0.01)
                        y = lerp(self.body_pose_t[i][1], newy, 0.01)

                    self.body_pose_t[i] = [int(x), int(y)]
                else:
                    x = RESOLUTION_X * (pose[0] - OFFSET_X) / DIMENSION_X
                    y = RESOLUTION_Y * (pose[1] - OFFSET_Y) / DIMENSION_Y
                    self.body_pose_t.append([int(x), int(y)])

        for parts in self.body_junctions:
            for pair in parts:
                # if (
                #     self.body_pose_t[pair[0]][1] > 0
                #     and self.body_pose_t[pair[1]][1] > 0
                #     and (self.show_head or (pair[1] > 10 and pair[0] > 10))
                #     and (
                #         self.show_wrist
                #         or ([17, 18, 19, 20] not in pair[0])
                #         and [17, 18, 19, 20, 21, 22] not in (pair[1])
                #     )
                # ):
                #     print(self.body_pose_t[pair[1]])
                #     print(self.body_pose_t[pair[0]])

                image = cv2.line(
                    image,
                    self.body_pose_t[pair[0]],
                    self.body_pose_t[pair[1]],
                    self.color,
                    self.thickness,
                )
        return image


class DisplayResult:
    """Displays the mirrored information on an opencv window"""

    def __init__(self):
        self.window_name = "draw"
        self.body = DrawPose()

    def run(self):
        """Updates the image with the informations"""
        while 1:
            image = np.zeros((RESOLUTION_Y, RESOLUTION_X, 3), dtype=np.uint8)
            data = data_queue.get()
            image = self.body.draw(image, data)
            # print(image.shape)
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(
                self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
            )
            cv2.imshow(self.window_name, image)
            key = cv2.waitKey(1)
            if key == 27:
                break


class PifpafProvider(threading.Thread):
    """
    (Thread)
    * Body pose from pifpaf
    TODO: Select the person
    """

    def __init__(self, threadID, feed):
        # * Home made hand signs : https://github.com/Thomas-Jld/gesture-recognition
        import get_hand_sign as ghs
        import get_pifpaf as gpp

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.processor = gpp.init()
        self.sign_provider = ghs.init()
        self.data = {}

    def run(self):
        import get_hand_sign as ghs
        import get_pifpaf as gpp
        from get_reflection import project

        print(
            """
        -------------------------------------
        Pifpaf running
        -------------------------------------
        """
        )

        while 1:
            if not PAUSED:
                start_t = time.time()
                if color is not None and depth is not None:
                    self.data = gpp.find_all_poses(self.processor, color, WINDOW)

                    if bool(self.data["body_pose"]):
                        eyes = self.data["body_pose"][0]

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


@sio.on("update")
def update(*_) -> None:
    """
    * Sends data to the client upon request
    """
    data_queue.get()
    sio.emit("global_data", global_data)


@sio.event
def connect(*args):
    """On connection, displays the id of the new client"""
    global client
    print(f"New client: {args[0]}")
    client = args[0]


# * Init everything when starting the program
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
    for name in functionalities.keys():
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
        print(
            """
        -------------------------------------
        Displaying
        -------------------------------------
        """
        )
        display = DisplayResult()
        display.run()
