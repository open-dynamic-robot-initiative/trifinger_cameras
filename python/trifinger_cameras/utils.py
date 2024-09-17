"""Utility functions."""

from __future__ import annotations

import typing

import cv2
import numpy as np
import tabulate


if typing.TYPE_CHECKING:
    from trifinger_cameras.py_tricamera_types import TriCameraInfo


def rodrigues_to_matrix(rvec):
    """Convert Rodrigues vector to homogeneous transformation matrix.

    Args:
        rvec (array-like):  Rotation in Rodrigues format as returned by OpenCV.

    Returns:
        quaternion (array-like):  Given rotation as a 4x4 homogeneous
        transformation matrix.
    """
    rvec = np.asarray(rvec)

    # convert the Rodrigues vector to a quaternion
    rotation_matrix = np.identity(4)
    rotation_matrix[:3, :3], _ = cv2.Rodrigues(rvec)

    return rotation_matrix


def convert_image(raw_image, format: str = "bgr") -> np.ndarray:
    """Convert raw image from camera observation.

    Args:
        raw_image: Raw image from camera observation.
        format (str): Format of the output image.  One of "bgr", "rgb", "gray".
            Defaults to "bgr" which is the default format of OpenCV.

    Returns:
        The converted image as NumPy array.
    """
    image = np.array(raw_image, copy=False)

    if format == "bgr":
        image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
    elif format == "rgb":
        image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2RGB)
    elif format == "gray":
        image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2GRAY)
    else:
        raise ValueError("Output format '%s' is not supported" % format)

    return image


def check_image_sharpness(
    image: np.ndarray,
    canny_threshold1: float = 25.0,
    canny_threshold2: float = 250.0,
) -> typing.Tuple[float, np.ndarray]:
    """Estimate sharpness of the given image, using edge detection.

    Uses Canny edge detection to estimate how sharp the images are
    (more edges = sharper).  If the mean value of the edge image is below a
    certain threshold, this might mean that the corresponding camera is out of
    focus and should be checked.

    See https://stackoverflow.com/a/66557408

    Args:
        image: Input image.
        canny_threshold1: See ``cv2.Canny``.
        canny_threshold2: See ``cv2.Canny``.

    Returns:
        Tuple (edge_mean, edge_image).  Where edge_mean is the mean value of the edge
        image.  A higher mean value means more edges and thus indicates a sharper image.
        edge_image shows the detected edges.  It is returned mostly for debugging and
        visualisation purposes.
    """
    edge_image = cv2.Canny(image, canny_threshold1, canny_threshold2)
    edge_mean = np.mean(edge_image)

    return edge_mean, edge_image


def print_tricamera_sensor_info(tricamera_info: TriCameraInfo) -> None:
    """Pretty-print the sensor info struct of the TriCamera driver."""
    camera_names = ["camera60", "camera180", "camera300"]

    camera_info = [
        (
            info.frame_rate_fps,
            f"{info.image_width}x{info.image_height}",
            info.camera_matrix,
            info.distortion_coefficients,
            info.tf_world_to_camera,
        )
        for info in tricamera_info.camera
    ]
    # add headers
    camera_info = [
        ("fps", "resolution", "camera_matrix", "distortion", "tf_world_to_camera"),
        *camera_info,
    ]
    # transpose the list for printing (so it's one column per camera)
    camera_info = list(map(tuple, zip(*camera_info)))

    with np.printoptions(precision=3, suppress=True):
        print(
            tabulate.tabulate(camera_info, headers=camera_names, tablefmt="pipe"),
            "\n",
        )
