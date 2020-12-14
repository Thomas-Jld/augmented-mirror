# Source : https://google.github.io/mediapipe/solutions/hands.html

import cv2
import numpy as np
import mediapipe as mp


# For webcam input:


def init():
    mp_hands = mp.solutions.hands
    return mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.4)


def find_hand_pose(hands, frame):
    image = frame.copy()
    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)
    hands_landmarks = []
    if results.multi_hand_landmarks:
        for hands in results.multi_hand_landmarks:
            hand_landmarks = []
            for landmark in hands.landmark:
                hand_landmarks.append([
                    (landmark.x-0.5)*frame.shape[0],
                    (landmark.y-0.5)*frame.shape[1],
                    landmark.presence,
                    landmark.visibility,
                    ])
            hands_landmarks.append(hand_landmarks)
            
    return hands_landmarks