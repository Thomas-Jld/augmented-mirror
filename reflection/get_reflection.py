import numpy as np
import pyrealsense2 as rs
import math


def get_depth(point: list, depth_frame, r: int) -> float:
    x = int(point[0])
    y = int(point[1])
    return np.mean(depth_frame[y - r : y + r, x - r : x + r])


def map_location(point: list, eyes: list, video_provider, depth_frame, r: int = 3):
    da = get_depth(eyes, depth_frame, 4) # Depth of the eye
    db = get_depth(point, depth_frame, r) # Depth of the point

    xa, ya, _ = rs.rs2_deproject_pixel_to_point(
        video_provider.depth_intrinsics, 
        eyes , 
        da)
    xb, yb, _ = rs.rs2_deproject_pixel_to_point(
        video_provider.color_intrinsics, 
        point, 
        db)

    dz = db + da
    dy = yb - ya
    dx = xb - xa
    if dz != 0:
        yi = ya + (da / dz) * dy
        xi = xa + (da / dz) * dx
        if not math.isnan(xi) and not math.isnan(yi):
            return [round(xi), round(yi)]

    return [-1, -1]

def project(points: list, eyes: list, video_provider, depth_frame):
    projected = []
    for i,point in enumerate(points):
        if bool(point[2:4]):
            projected.append([point[0:2] + map_location(point[2:4], eyes, video_provider, depth_frame), get_depth(point[2:4], depth_frame, 4)])
    return projected