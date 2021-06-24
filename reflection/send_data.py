import socketio
import threading
import time
import numpy as np

sio = socketio.Client(engineio_logger=False )


"""
Works as a queue to add data in the global DATA variable
TODO: Use a real Queue instead of this function
"""
def add_data(name, data):
    global AVAILABLE
    if not AVAILABLE:
        while not AVAILABLE:
            time.sleep(NAP)
    else:
        AVAILABLE = False

    DATA[name] = data

    AVAILABLE = True



"""
A class that reads frames from the intel Realsense D435I Camera (color and depth frames)
"""
class IntelVideoReader(object):
    def __init__(self):
        import pyrealsense2 as rs
        
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

        color_frame = np.fliplr(np.asanyarray(color_frame.get_data()))
        depth_frame = np.fliplr(np.asanyarray(depth_frame.get_data()))

        return [color_frame, depth_frame]
        
"""
A class that reads frames from the webcam (color only)
"""
class CameraVideoReader:
    def __init__(self):
        import cv2 as cv
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

"""
A thread that reads frames using the 2 previous classes' functions 
and stores them into global variables. (global) depth will be none if
the camera isn't the D435
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
        while 1:
            global color 
            global depth
            color, depth = self.feed.next_frame() #Updates global variales
            time.sleep(1/(2*FPS)) # Runs faster to be sure to get the 


"""
A thread that gets body pose from lightweight pose estimation
"""
class BodyProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_body_pose as gbp

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed

    def run(self):
        import get_body_pose as gbp # Import the code from another python file if the cwd
        print(
        """
        -------------------------------------
        Body pose running
        -------------------------------------
        """)
        self.pose = gbp.init()
        while 1:
            start_t = time.time() # Used to mesure the elapsed time of each loop

            if color is not None and depth is not None:
                self.data = gbp.find_body_pose(self.pose, color) # Infer on image

                add_data("body_pose", self.data) # Stores the data through the availability queue

            end_t = time.time()
            dt = 1/FPS - (end_t - start_t) if (end_t - start_t) < 1/FPS else 0.01
            time.sleep(dt) # Sleeps for 1/FPS (e.g: 33ms if FPS=60) if the code is fast enough, else 10 ms


"""
A thread that gets body mesh from detectron
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
            dt = max(1/FPS - (end_t - start_t), 0)
            time.sleep(dt)

"""
Body pose from mediapipe
TODO: Crop the image to only get the center
"""
class HolisticProvider(threading.Thread):
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
                dt = max(1/FPS - (end_t - start_t), 0)
                time.sleep(dt)
            else:
                time.sleep(5)


class PifpafProvider(threading.Thread):
    def __init__(self, threadID, feed):
        import get_pifpaf as gpp

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = feed
        self.processor = gpp.init()

    def run(self):
        import get_pifpaf as gpp
        # from get_reflection import project
        print(
        """
        -------------------------------------
        Pifpaf running
        -------------------------------------
        """)
        count = 0
        start = time.time()
        while 1:
            if color is not None:
                gpp.find_all_poses(self.processor, color)
                count+=1
            if (now := time.time()) - start > 1:
                print(count)
                start = now
                count = 0
            


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
                dt = max(1/FPS - (end_t - start_t), 0)
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

    functionalities = {
        "body_pose": [False, BodyProvider], # Body pose, requires Face mesh
        "body_mesh": [False, BodyMeshProvider], # Body mesh, requires Body pose
        "hands_pose": [False, HandsProvider], # Hands, requires Body pose
        "face_mesh": [False, FaceProvider], # Face mesh
        "holistic_pose": [True, HolisticProvider], # Holistic, Body face and hands in one
        "pifpaf_pose": [False, PifpafProvider], # Pifpaf, Body face and hands in one
    }

    feed = CameraVideoReader()
    # feed = IntelVideoReader()

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

    FPS = 60
    NAP = 0.001

    PROJECT = True
    AVAILABLE = True
    CHANGED = True
    PAUSED = False
    
    sio.connect('http://0.0.0.0:5000')