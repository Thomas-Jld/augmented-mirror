import numpy as np
import pyrealsense2 as rs
import math

theta = math.pi/8

def get_depth(point: list, depth_frame, r: int) -> float:
    x = int(point[0])
    y = int(point[1])
    x = x if x >= 0 else 0
    x = x if x < len(depth_frame) else len(depth_frame[0])
    y = y if y >= 0 else 0
    y = y if y < len(depth_frame) else len(depth_frame)

    try:
        return np.float64(np.min(depth_frame[max(y - r, 0) : min(y + r, len(depth_frame)), max(x - r, 0) : min(x + r, len(depth_frame[0]))]))
    except:
        return np.float64(depth_frame[x, y])



def map_location(point: list, eyes: list, video_provider, depth_frame, r: int = 3):
    da = get_depth(eyes, depth_frame, 4) # Depth of the eye
    db = get_depth(point, depth_frame, r) # Depth of the point

    xa, ya, za = rs.rs2_deproject_pixel_to_point(
        video_provider.depth_intrinsics, 
        eyes , 
        da)
    xb, yb, zb = rs.rs2_deproject_pixel_to_point(
        video_provider.color_intrinsics, 
        point, 
        db)

    ya = ya*math.cos(theta) + za*math.sin(theta)
    yb = yb*math.cos(theta) + zb*math.sin(theta)
    
    dz = db + da
    dy = yb - ya
    dx = xb - xa
    if dz != 0:
        yi = ya + (da / dz) * dy
        xi = xa + (da / dz) * dx
        if not math.isnan(xi) and not math.isnan(yi):
            return [round(xi), round(yi)]

    return [-1, -1]

def project(points: list, eyes: list, video_provider, depth_frame, r):
    projected = []
    for i,point in enumerate(points):
        if bool(point[2:4]):
            projected.append(point[0:2] + map_location(point[2:4], eyes, video_provider, depth_frame, r) + [get_depth(point[2:4], depth_frame, r)])
    return projected