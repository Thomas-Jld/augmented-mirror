import numpy as np
import pyrealsense2 as rs
import math
from typing import List

theta = math.radians(13.8)


def get_depth(point: list, depth_frame, depth_radius: int) -> float:
    x = min(max(int(point[0]), 0), len(depth_frame[0]))
    y = min(max(int(point[1]), 0), len(depth_frame))
    # x = int(point[0])
    # y = int(point[1])
    # x = x if x >= 0 else 0
    # x = x if x < len(depth_frame[0]) else len(depth_frame[0])
    # y = y if y >= 0 else 0
    # y = y if y < len(depth_frame) else len(depth_frame)

    try:
        return np.float64(
            np.mean(
                depth_frame[
                    max(y - depth_radius, 0) : min(y + depth_radius, len(depth_frame)),
                    max(x - depth_radius, 0) : min(
                        x + depth_radius, len(depth_frame[0])
                    ),
                ]
            )
        )
    except:
        return np.float64(depth_frame[x, y])


def map_location(
    point: list,
    eyes_depth: int,
    eyes_coordinates: list,
    point_depth: int,
    video_provider,
) -> List[int]:
    da = eyes_depth
    db = point_depth
    xa, ya, za = eyes_coordinates

    xb, yb, zb = rs.rs2_deproject_pixel_to_point(
        video_provider.color_intrinsics, point, db
    )

    ya = ya * math.cos(theta) + za * math.sin(theta)
    yb = yb * math.cos(theta) + zb * math.sin(theta)

    dz = db + da
    dy = yb - ya
    dx = xb - xa
    if dz != 0:
        yi = ya + (da / dz) * dy
        xi = xa + (da / dz) * dx
        if not math.isnan(xi) and not math.isnan(yi):
            return [int(xi), int(yi)]

    return [-1, -1]


def project(
    points: List[List],
    eyes_position: list,
    video_provider,
    depth_frame,
    depth_radius,
    ref=0,
) -> List[List]:
    """Projects every keypoint in world coordinates based on the user's point of view"""

    projected = []
    eyes_depth = get_depth(eyes_position, depth_frame, 4)  # Depth of the eye
    eyes_coordinates = rs.rs2_deproject_pixel_to_point(
        video_provider.depth_intrinsics, eyes_position, eyes_depth
    )

    for i, point in enumerate(points):
        if bool(point):
            point_depth = (
                get_depth(point, depth_frame, depth_radius) if ref == 0 else ref
            )  # Depth of the point
            projected.append(
                map_location(
                    point=point,
                    eyes_depth=eyes_depth,
                    eyes_coordinates=eyes_coordinates,
                    point_depth=point_depth,
                    video_provider=video_provider,
                )
                + [point_depth]
            )
    return projected
