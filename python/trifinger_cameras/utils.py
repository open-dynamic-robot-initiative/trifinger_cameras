"""Utility functions."""
import numpy as np
import cv2
import tf


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
    rvec = np.asarray(rvec)

    rotation_matrix = rodrigues_to_matrix(rvec)
    quaternion = tf.transformations.quaternion_from_matrix(rotation_matrix)

    return quaternion
