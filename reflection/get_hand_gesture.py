# Source : https://google.github.io/mediapipe/solutions/hands.html

import cv2
import mediapipe as mp


def init():
    mp_hands = mp.solutions.hands
    return mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.6)


def find_hand_pose(hands, frame, window):
    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
    image = image[:, min_width:max_width]

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    results = hands.process(image)

    hands_landmarks = []

    if results.multi_hand_landmarks:
        for i, hands in enumerate(results.multi_hand_landmarks):
            hands_landmarks.append([])
            for j, landmark in enumerate(hands.landmark):
                hands_landmarks[-1].append(
                    [
                        (landmark.x - 0.5) * image.shape[1],
                        landmark.y * image.shape[0],
                    ]
                )

    return hands_landmarks
