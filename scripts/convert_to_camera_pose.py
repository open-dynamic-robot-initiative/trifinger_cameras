#!/usr/bin/env python3
"""
Takes as input the pose of a detected marker and returns the pose of the camera
relative to the marker in a format that can be used by TF.
"""
import argparse
import json

import numpy as np
from scipy.spatial.transform import Rotation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("marker_pose_json", type=str)
    args = parser.parse_args()

    marker_pose = json.loads(args.marker_pose_json)

    rvec = np.asarray(marker_pose["rvec"])
    tvec = np.asarray(marker_pose["tvec"])

    # Construct homogeneous transformation matrix based on rvec and tvec
    mat = np.identity(4)
    mat[:3, :3] = Rotation.from_rotvec(rvec).as_matrix()
    mat[:3, 3] = tvec.flatten()

    # What we get as input is "camera -> marker".  We want it the other way
    # round, so imply invert the matrix
    invmat = np.linalg.inv(mat)

    # Output as "x y z qx qy qz qw", the format that is used by tf's
    # static_transform_publisher.
    camera_translation = invmat[:3, 3]
    camera_quaternion = Rotation.from_matrix(invmat[:3, :3]).as_quat()
    print(
        ("{:.4f} " * 7).format(
            camera_translation[0],
            camera_translation[1],
            camera_translation[2],
            camera_quaternion[0],
            camera_quaternion[1],
            camera_quaternion[2],
            camera_quaternion[3],
        )
    )


if __name__ == "__main__":
    main()
