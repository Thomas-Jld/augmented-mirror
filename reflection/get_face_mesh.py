# Source : https://google.github.io/mediapipe/solutions/face_mesh.html

import cv2
import mediapipe as mp


def init():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def find_face_mesh(face, frame):
    image = frame.copy()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    face = init()
    results = face.process(image)
    face.close()

    faces_landmarks = []

    if results.multi_face_landmarks:
        for i, faces in enumerate(results.multi_face_landmarks):
            for j, face_landmarks in enumerate(faces.landmark):
                faces_landmarks.append([
                    i,
                    j,
                    face_landmarks.x*frame.shape[1],
                    face_landmarks.y*frame.shape[0],
                ])

    return faces_landmarks
