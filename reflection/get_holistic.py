# Source : https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp


def init():
    mp_holistic = mp.solutions.holistic
    return mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def find_all_poses(holistic, frame):
    image = frame.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    results = holistic.process(image)

    body_landmarks = []

    if results.pose_landmarks:
        for j, landmark in enumerate(results.pose_landmarks.landmark):
            body_landmarks.append([
                0,
                j,
                int(landmark.x*frame.shape[1]), 
                int(landmark.y*frame.shape[0]),
                ])
    
    faces_landmarks = []

    if results.face_landmarks:
        for j, landmark in enumerate(results.face_landmarks.landmark):
            faces_landmarks.append([
                0, 
                j, 
                int(landmark.x*frame.shape[1]), 
                int(landmark.y*frame.shape[0]),
            ])

    left_hands_landmarks = []

    if results.left_hand_landmarks:
        for j, landmark in enumerate(results.left_hand_landmarks.landmark):
            left_hands_landmarks.append([
                0,
                j,
                int(landmark.x*frame.shape[1]), 
                int(landmark.y*frame.shape[0]),
                ])
                
    right_hands_landmarks = []

    if results.right_hand_landmarks:
        for j, landmark in enumerate(results.right_hand_landmarks.landmark):
            right_hands_landmarks.append([
                0,
                j,
                int(landmark.x*frame.shape[1]), 
                int(landmark.y*frame.shape[0]),
                ])

    return {"face_mesh": faces_landmarks, 
            "body_pose": body_landmarks, 
            "right_hand_pose": left_hands_landmarks, 
            "left_hand_pose": right_hands_landmarks,}