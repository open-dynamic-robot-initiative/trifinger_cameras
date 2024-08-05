"""Utility functions."""

import typing

import cv2
import numpy as np


def rodrigues_to_matrix(rvec):
    """Convert Rodrigues vector to homogeneous transformation matrix

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
