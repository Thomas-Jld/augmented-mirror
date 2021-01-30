# Source : https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp


def init():
    mp_pose = mp.solutions.pose
    return mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def find_body_pose(pose, frame):
    image = frame.copy()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    pose = init()
    results = pose.process(image)
    pose.close()

    body_landmarks = []

    if results.pose_landmarks:
        for i, bodies in enumerate(results.pose_landmarks):
            for j, landmark in enumerate(bodies.landmark):
                body_landmarks.append([
                    i,
                    j,
                    landmark.x*frame.shape[1], 
                    landmark.y*frame.shape[0],
                    ])

    return body_landmarks