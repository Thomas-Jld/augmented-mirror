# Source : https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp


def init():
    mp_pose = mp.solutions.pose
    return mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def find_body_pose(pose, frame, window):
    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
    image = image[:, min_width:max_width]

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    results = pose.process(image)

    body_landmarks = []

    if results.pose_landmarks:
        for i, bodies in enumerate(results.pose_landmarks):
            body_landmarks.append([])
            for j, landmark in enumerate(bodies.landmark):
                body_landmarks[-1].append(
                    [
                        min_width + landmark.x * image.shape[1],
                        landmark.y * image.shape[0],
                    ]
                )

    return body_landmarks
