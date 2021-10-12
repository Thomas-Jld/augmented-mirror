# Source : https://google.github.io/mediapipe/solutions/face_mesh.html

import cv2
import mediapipe as mp


def init():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )


def find_face_mesh(face, frame, window):
    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
    image = image[:, min_width:max_width]

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    results = face.process(image)

    faces_landmarks = []

    if results.multi_face_landmarks:
        for i, faces in enumerate(results.multi_face_landmarks):
            faces_landmarks.append([])
            for j, face_landmarks in enumerate(faces.landmark):
                faces_landmarks[-1].append(
                    [
                        i,
                        j,
                        min_width + face_landmarks.x * image.shape[1],
                        face_landmarks.y * image.shape[0],
                    ]
                )

    return faces_landmarks
