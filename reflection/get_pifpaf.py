import openpifpaf

from openpifpaf.predictor import Predictor

def init():
    predictor = Predictor(
        visualize_image=False,
        visualize_processed_image=False,
        # checkpoint="shufflenetv2k30-wholebody",
        checkpoint="shufflenetv2k16-wholebody",
        )

    return predictor


def find_all_poses(predictor, frame):
    pred, _, meta = predictor.numpy_image(frame)
    results = [ann.json_data() for ann in pred]

    if(len(results) == 0):
        return {"face_mesh": [], 
                "body_pose": [], 
                "right_hand_pose": [], 
                "left_hand_pose": [],}
    else:
        results = results[0]["keypoints"]
        results = [[results[3*i], results[3*i+1], results[3*i+2]] for i in range(int(len(results)/3))]

    body_landmarks = []
    for j, landmark in enumerate(results[0: 17]):
        body_landmarks.append([
            0,
            j,
            int(landmark[0]),
            int(landmark[1]),
            ])
    
    faces_landmarks = []
    for j, landmark in enumerate(results[23: 91]):
        faces_landmarks.append([
            0,
            j,
            int(landmark[0]),
            int(landmark[1]),
            ])

    left_hands_landmarks = []
    for j, landmark in enumerate(results[91: 112]):
        left_hands_landmarks.append([
            0,
            j,
            int(landmark[0]),
            int(landmark[1]),
            ])

    right_hands_landmarks = []
    for j, landmark in enumerate(results[112: 133]):
        right_hands_landmarks.append([
            0,
            j,
            int(landmark[0]),
            int(landmark[1]),
            ])

    return {"face_mesh": faces_landmarks, 
            "body_pose": body_landmarks, 
            "right_hand_pose": left_hands_landmarks, 
            "left_hand_pose": right_hands_landmarks,}
    # return [[[x,y,c] for x,y,c in [part for part in ann.data]] for ann in pred]