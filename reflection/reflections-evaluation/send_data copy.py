import socketio
import threading
import time


import get_reflection as gr
# import get_temperature as gt

sio = socketio.Client(engineio_logger=True)

class VideoReader(object):
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
        

class frame_provider(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.feed = VideoReader()

    def run(self):
        while 1:
            color, depth = self.feed.next_frame()
            time.sleep(0.033)


class joint_provider(threading.Thread):
    def __init__(self, threadID, net):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.net = net

    def run(self):
        while 1:
            if color and depth:
                self.data = gr.find_reflection(self.net, color, depth)
                if self.data:
                    sio.emit("reflection", self.data)
                else:
                    time.sleep(0.02)
            else:
                time.sleep(0.03)



@sio.event
def connect():
    print('Connected to the server')
    net = gr.init()
    Thread1 = frame_provider("frame")
    Thread2 = joint_provider("joint", net)

    Thread1.start()
    Thread2.start()



if __name__ == '__main__':
    color = None
    depth = None
    threads = []
    sio.connect('http://0.0.0.0:5000')
