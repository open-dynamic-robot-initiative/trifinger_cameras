#!/usr/bin/python
"""Convert a Rodrigues vector to a quaternion."""
import argparse
import numpy as np
import cv2
import tf

from trifinger_cameras import utils


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("v1", type=float)
    parser.add_argument("v2", type=float)
    parser.add_argument("v3", type=float)
    args = parser.parse_args()

    rvec = np.array([args.v1, args.v2, args.v3])

    quaternion = utils.rodrigues_to_quaternion(rvec)
    euler = tf.transformations.euler_from_quaternion(quaternion)

    print("Euler: {}".format(euler))
    print("Quaternion: {}".format(quaternion))


if __name__ == "__main__":
    main()
