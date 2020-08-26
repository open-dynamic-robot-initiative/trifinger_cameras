"""Utility functions."""
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


def rodrigues_to_quaternion(rvec):
    """Convert Rodrigues vector to quaternion

    Args:
        rvec (array-like):  Rotation in Rodrigues format as returned by OpenCV.

    Returns:
        quaternion (array-like):  Given rotation as a quaternion `[x, y, z, w]`
    """
    # this import is moved due to versions differences in python2 (ros)
    # and python3 (opencv)
    import tf

    rvec = np.asarray(rvec)

    rotation_matrix = rodrigues_to_matrix(rvec)
    quaternion = tf.transformations.quaternion_from_matrix(rotation_matrix)

    return quaternion


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
