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
    return [ann.json_data() for ann in pred]
    # return [[[x,y,c] for x,y,c in [part for part in ann.data]] for ann in pred]