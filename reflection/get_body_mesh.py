#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import sys
import os
import glob
import pickle
from typing import Any, ClassVar, Dict, List
import torch
import cv2
import numpy as np
import time


from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.engine.defaults import DefaultPredictor
from detectron2.structures.boxes import BoxMode
from detectron2.structures.instances import Instances
from detectron2.utils.logger import setup_logger

sys.path.append(os.path.join(os.path.dirname(__file__), "detectron2/projects/DensePose"))
from densepose import add_densepose_config, add_hrnet_config
from densepose.utils.logger import verbosity_to_level
from densepose.vis.base import CompoundVisualizer
from densepose.vis.bounding_box import ScoredBoundingBoxVisualizer
from densepose.vis.densepose_results import (
    DensePoseResultsContourVisualizer,
    DensePoseResultsFineSegmentationVisualizer,
    DensePoseResultsUVisualizer,
    DensePoseResultsVVisualizer,
)
from densepose.vis.extractor import CompoundExtractor, create_extractor

config_path = "configs/densepose_rcnn_R_50_FPN_s1x.yaml"
model_path = "models/model_final_162be9.pkl"
VISUALIZERS: ClassVar[Dict[str, object]] = {
    "dp_contour": DensePoseResultsContourVisualizer,
    "dp_segm": DensePoseResultsFineSegmentationVisualizer,
    "dp_u": DensePoseResultsUVisualizer,
    "dp_v": DensePoseResultsVVisualizer,
    "bbox": ScoredBoundingBoxVisualizer,
}


def setup_config(config_fpath: str, model_fpath: str, opts: List[str]):
    opts.append("MODEL.ROI_HEADS.SCORE_THRESH_TEST")
    opts.append(0.8) # Min score
    cfg = get_cfg()
    add_densepose_config(cfg)
    add_hrnet_config(cfg)
    cfg.merge_from_file(config_fpath)
    if opts:
        cfg.merge_from_list(opts)
    cfg.MODEL.WEIGHTS = model_fpath
    cfg.freeze()
    return cfg


def create_context() -> Dict[str, Any]:
    vis_specs = ["dp_contour"]
    visualizers = []
    extractors = []
    for vis_spec in vis_specs:
        vis = VISUALIZERS[vis_spec]()
        visualizers.append(vis)
        extractor = create_extractor(vis)
        extractors.append(extractor)
    visualizer = CompoundVisualizer(visualizers)
    extractor = CompoundExtractor(extractors)
    context = {
        "extractor": extractor,
        "visualizer": visualizer,
        "entry_idx": 0,
    }
    return context


def execute_on_outputs(context: Dict[str, Any], entry: Dict[str, Any], outputs):
    visualizer = context["visualizer"]
    extractor = context["extractor"]
    image = cv2.cvtColor(entry["image"], cv2.COLOR_BGR2GRAY)
    image = np.tile(image[:, :, np.newaxis], [1, 1, 3])
    data = extractor(outputs)
    return visualizer.visualize(np.zeros((image.shape[0],image.shape[1],3), np.uint8) , data)


def init_densepose():
    print(f"Loading config from {config_path}")
    print(f"Loading model from {model_path}")
    opts = []
    global cfg
    cfg = setup_config(config_path, model_path, opts)
    global predictor
    predictor = DefaultPredictor(cfg)
    global context
    context = create_context()


def infere_on_image(image):
    img = np.asarray(image)

    with torch.no_grad():
        outputs = predictor(img)["instances"]

        return execute_on_outputs(context, {"image": img}, outputs)

