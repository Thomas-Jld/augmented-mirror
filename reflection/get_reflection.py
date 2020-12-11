import argparse

import sys
import os
import cv2
import numpy as np
import torch
import pyrealsense2 as rs
import json
import math


sys.path.append(os.path.join(os.path.dirname(__file__), "pose-estimation"))
from models.with_mobilenet import PoseEstimationWithMobileNet
from modules.keypoints import extract_keypoints, group_keypoints
from modules.load_state import load_state
from modules.pose import Pose
from val import normalize, pad_width









def infer_fast(net, img, net_input_height_size, stride, upsample_ratio, cpu,
               pad_value=(0, 0, 0), img_mean=(128, 128, 128), img_scale=1/256):
    """
    Scale the image and estimate the probabilty of each point being a keypoint (heatmap)
    """
    height, width, _ = img.shape
    scale = net_input_height_size / height

    scaled_img = cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    scaled_img = normalize(scaled_img, img_mean, img_scale)
    min_dims = [net_input_height_size, max(scaled_img.shape[1], net_input_height_size)]
    padded_img, pad = pad_width(scaled_img, stride, pad_value, min_dims)

    tensor_img = torch.from_numpy(padded_img).permute(2, 0, 1).unsqueeze(0).float()
    if not cpu:
        tensor_img = tensor_img.cuda()

    stages_output = net(tensor_img)

    stage2_heatmaps = stages_output[-2]
    heatmaps = np.transpose(stage2_heatmaps.squeeze().cpu().data.numpy(), (1, 2, 0))
    heatmaps = cv2.resize(heatmaps, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    stage2_pafs = stages_output[-1]
    pafs = np.transpose(stage2_pafs.squeeze().cpu().data.numpy(), (1, 2, 0))
    pafs = cv2.resize(pafs, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    return heatmaps, pafs, scale, pad




def get_depth(pose, joint: int, depth_frame) -> float:
    x = int(pose.keypoints[joint][0])
    y = int(pose.keypoints[joint][1])
    return np.mean(depth_frame[y - 3 : y + 3, x - 3 : x + 3])


# def get_position(pose, joint, depth_frame, width, height):
#     """
#     Calculates the position of a joint in space with the camera as reference
#     """
#     depth = get_depth(pose, joint, depth_frame)
#     xp, yp = pose.keypoints[pose]
#     fovh = 86
#     fovv = 57
#     return x, y


def get_ratio(pose, data : dict, width: int, height: int, depth_frame, video_provider):
    xa, ya, za = rs.rs2_deproject_pixel_to_point(
        video_provider.depth_intrinsics, 
        [pose.keypoints[0][0], pose.keypoints[0][1]],
        get_depth(pose, 0, depth_frame))
    
    count = 0
    ratios = []
    for name, coords in data.items():
        n = pose.kpt_names.index(name)
        if coords != -1 and n > 1 and n < 14:
            count += 1 
            d = get_depth(pose, n, depth_frame) # Depth of the joint
            x, y, _ = rs.rs2_deproject_pixel_to_point(video_provider.depth_intrinsics, [pose.keypoints[n][0], pose.keypoints[n][1]] , d)
            ratios.append([x/(pose.keypoints[n][0] - width/2), y/(pose.keypoints[n][1] - height/2)])
    
    ratios = np.array(ratios)
    if len(ratios) == 0:
        return [1, 1, 0, 0, 1/2]
    return [sum(ratios[:, 0])/count, sum(ratios[:, 1])/count, -xa, ya, 1/2]


def map_location(pose, joint: int, width: int, height: int, depth_frame, video_provider):
    da = get_depth(pose, 0, depth_frame) # Depth of the nose ~ eyes
    db = get_depth(pose, joint, depth_frame) # Depth of the joint

    # xa, ya = get_position(pose, 0, depth_frame, width, height)
    # xb, yb = get_position(pose, joint , depth_frame, width, height)

    xa, ya, za = rs.rs2_deproject_pixel_to_point(video_provider.depth_intrinsics, [pose.keypoints[0][0], pose.keypoints[0][1]] , da)
    xb, yb, zb = rs.rs2_deproject_pixel_to_point(video_provider.color_intrinsics, [pose.keypoints[joint][0], pose.keypoints[joint][1]], db)

    # dxa = (da**2 - xa**2)**.5
    # dya = (da**2 - ya**2)**.5
    #
    # dxb = (db**2 - xb**2)**.5
    # dyb = (db**2 - yb**2)**.5
    #
    # aapx = (dxa**2 - ya**2)**.5
    # bbpx = (dxb**2 - yb**2)**.5
    #
    # aapy = (dya**2 - xa**2)**.5
    # bbpy = (dyb**2 - xb**2)**.5
    #
    # rx = (yb-ya)*((aapx + ((yb - ya)*(aapx)**.5/(aapx**.5 + bbpx**.5))**.5)/((yb-ya)**2 +aapx**.5 + bbpx**.5)) + ya - offset
    # ry = (xb-xa)*((aapy + ((xb - xa)*(aapy)**.5/(aapy**.5 + bbpy**.5))**.5)/((xb-xa)**2 +aapy**.5 + bbpy**.5)) + xa - offset

    dz = db + da
    dy = yb - ya
    dx = xb - xa
    if dz != 0:
        yi = ya + (da / dz) * dy
        xi = xa + (da / dz) * dx
        if not math.isnan(xi) and not math.isnan(yi):
            return [round(xi), round(yi)]

    return -1


def find_reflection(net, img, depth, image_provider, send = False, cpu = False):

    height_size = 256
    stride = 8
    upsample_ratio = 4
    num_keypoints = Pose.num_kpts

    data = {}

    """
    Estimate the pose and find the person in the middle
    """

    heatmaps, pafs, scale, pad = infer_fast(net, img, height_size, stride, upsample_ratio, cpu)

    total_keypoints_num = 0
    all_keypoints_by_type = []
    for kpt_idx in range(num_keypoints):  # 19th for bg
        total_keypoints_num += extract_keypoints(heatmaps[:, :, kpt_idx], all_keypoints_by_type, total_keypoints_num)

    pose_entries, all_keypoints = group_keypoints(all_keypoints_by_type, pafs, demo=True)
    for kpt_id in range(all_keypoints.shape[0]):
        all_keypoints[kpt_id, 0] = (all_keypoints[kpt_id, 0] * stride / upsample_ratio - pad[1]) / scale
        all_keypoints[kpt_id, 1] = (all_keypoints[kpt_id, 1] * stride / upsample_ratio - pad[0]) / scale
    current_poses = []

    distMin = 310
    midPose = None

    for n in range(len(pose_entries)):
        if len(pose_entries[n]) == 0:
            continue
        pose_keypoints = np.ones((num_keypoints, 2), dtype=np.int32) * -1
        for kpt_id in range(num_keypoints):
            if pose_entries[n][kpt_id] != -1.0:  # keypoint was found
                pose_keypoints[kpt_id, 0] = int(all_keypoints[int(pose_entries[n][kpt_id]), 0])
                pose_keypoints[kpt_id, 1] = int(all_keypoints[int(pose_entries[n][kpt_id]), 1])
        pose = Pose(pose_keypoints, pose_entries[n][18])

        dist = abs(pose.keypoints[0][0] - image_provider.width/2)
        if dist < distMin:
            distMin = dist
            midPose = pose
        current_poses.append(pose)

    """
    Find the depth of each exposed parts of the body
    """

    if midPose != None:
        for n in range(len(Pose.kpt_names)):
            if midPose.keypoints[n][0] != 0 or midPose.keypoints[n][1] != 0:
                data[Pose.kpt_names[n]] = map_location(
                    midPose, n, image_provider.width, image_provider.height,
                    depth, image_provider
                )
            
        data["ratio"] = get_ratio(
            midPose, data, image_provider.width, image_provider.height,
            depth, image_provider
        )
    return data

def init(cpu = False):
    net = PoseEstimationWithMobileNet()

    checkpoint_path = "pose-estimation/checkpoint_iter_370000.pth"
    checkpoint = torch.load(checkpoint_path, map_location='cpu') #load the existing model
    load_state(net, checkpoint)

    net = net.eval()
    if not cpu:
        net = net.cuda()

    return net

