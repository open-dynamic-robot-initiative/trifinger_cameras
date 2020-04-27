#!/usr/bin/env python3
"""
This demo is to start a camera and display the images from it
as a non-real time livestream.

Basically illustrates what objects to create to interact with the
camera, and the available methods for that.
"""
import argparse
import numpy as np
import cv2

import trifinger_cameras


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    arg_action_group = argparser.add_mutually_exclusive_group(required=False)
    arg_action_group.add_argument(
        "--pylon",
        action="store_true",
        help="""Access the camera via Pylon.  If not set, OpenCV is used.""",
    )
    args = argparser.parse_args()

    camera_data = trifinger_cameras.camera.Data()
    if args.pylon:
        camera_driver = trifinger_cameras.camera.PylonDriver("cam_1")
    else:
        camera_driver = trifinger_cameras.camera.OpenCVDriver(0)

    camera_backend = trifinger_cameras.camera.Backend(
        camera_driver, camera_data
    )
    camera_frontend = trifinger_cameras.camera.Frontend(camera_data)

    while True:
        observation = camera_frontend.get_latest_observation()
        window_name = "Image Stream"
        cv2.imshow(window_name, np.array(observation.image, copy=False))
        cv2.waitKey(3)


if __name__ == "__main__":
    main()
