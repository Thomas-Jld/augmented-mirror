import os
import json

import cv2
import mediapipe as mp
import numpy as np
import youtube_dl

url = "https://www.youtube.com/watch?v=Pd2KM3qjcKk"
base = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base, "video/")
file_name = "test"
count = 0


def process(url: str):
    global count
    mp_pose = mp.solutions.pose

    ydl_opts = {
        "outtmpl": os.path.join(data_path, f"{file_name}_input.mp4"),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    cap = cv2.VideoCapture(os.path.join(data_path, f"{file_name}_input.mp4"))
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    # for i in range(4100):
    #     cap.read()
    #     count += 1

    width = cap.get(3)
    height = cap.get(4)
    size = (int(width), int(height))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"FPS: {fps} RES: {size}")
    out = cv2.VideoWriter(
        os.path.join(data_path, f"{file_name}.mp4"),
        cv2.VideoWriter_fourcc(*"MP4V"),
        fps,
        size,
    )

    body_landmarks = {}
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        enable_segmentation=True,
    ) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            image.flags.writeable = False
            try:
                results = pose.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.segmentation_mask is not None:
                    condition = (
                        np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
                    )
                    bg_image = np.zeros(image.shape, dtype=np.uint8)
                    image = np.where(condition, image, bg_image)
                else:
                    image = np.zeros(image.shape, dtype=np.uint8)
            except:
                pose = mp_pose.Pose(
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                    enable_segmentation=True,
                )
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # print(count)

            if results.pose_landmarks:
                body_landmarks[count] = []
                # for i, bodies in enumerate(results.pose_landmarks):
                for landmark in results.pose_landmarks.landmark:
                    body_landmarks[count].append(
                        [
                            int(landmark.x * image.shape[1]),
                            int(landmark.y * image.shape[0]),
                        ]
                    )

            out.write(image)
            cv2.imshow("MediaPipe Pose", image)
            count += 1
            if cv2.waitKey(5) & 0xFF == 27 or count >= frame_count:
                with open(f"{file_name}.json", "w+") as f:
                    json.dump(body_landmarks, f)
                out.release()
                break
        cap.release()


process(url)
