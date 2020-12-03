"""Utility functions."""
import cv2
import numpy as np


def rot_points(rmat, points):

    N = points.shape[0]

    for i in np.arange(N):
        points[i, :] = np.matmul(rmat, points[i, :])

    return points


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
