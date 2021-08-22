# Source : https://google.github.io/mediapipe/solutions/hands.html

import cv2
import mediapipe as mp


def init():
    mp_hands = mp.solutions.hands
    return mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.4)


def find_hand_pose(hands, frame):
    image = frame.copy()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    hands = init()
    results = hands.process(image)
    hands.close()

    hands_landmarks = []

    if results.multi_hand_landmarks:
        for i, hands in enumerate(results.multi_hand_landmarks):
            hands_landmarks.append([])
            for j, landmark in enumerate(hands.landmark):
                hands_landmarks[-1].append([
                    i,
                    j,
                    landmark.x*frame.shape[0],
                    landmark.y*frame.shape[1],
                    ])

    return hands_landmarks
