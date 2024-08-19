#!/usr/bin/env python3
"""
This demo is to start a camera and display the images from it
as a non-real time livestream.

Basically illustrates what objects to create to interact with the
camera, and the available methods for that.
"""

import argparse
import pathlib
import sys

import cv2
import numpy as np

import trifinger_cameras
from trifinger_cameras import utils


def main() -> int:  # noqa: D103
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--pylon",
        action="store_true",
        help="""Access the camera via Pylon.  If not set, OpenCV is used.""",
    )
    argparser.add_argument(
        "--camera-id",
        "-c",
        default="",
        help="""ID of the camera that is used.  If --pylon is set this refers
            to the DeviceUserId, otherwise it is the index of the device.
        """,
    )
    argparser.add_argument(
        "--camera-info",
        type=pathlib.Path,
        metavar="<file>",
        dest="camera_info_file",
        help="Path to YAML file with camera calibration data.",
    )
    argparser.add_argument(
        "--multi-process",
        action="store_true",
        help="""If set, run only front end with multi-process robot data.  Otherwise run
            everything within a single process.
        """,
    )
    argparser.add_argument(
        "--record",
        type=str,
        help="""Path to file in which camera data is recorded.""",
    )

    args = argparser.parse_args()

    if args.multi_process:
        # In multi-process case assume that the backend is running in a
        # separate process and only set up the frontend here.
        camera_data = trifinger_cameras.camera.MultiProcessData("camera", False)
    else:
        camera_data = trifinger_cameras.camera.SingleProcessData()

        try:
            if args.pylon:
                if args.camera_info_file:
                    camera_driver = trifinger_cameras.camera.PylonDriver(
                        args.camera_info_file
                    )
                else:
                    camera_driver = trifinger_cameras.camera.PylonDriver(args.camera_id)
            else:
                camera_id = int(args.camera_id) if args.camera_id else 0
                camera_driver = trifinger_cameras.camera.OpenCVDriver(camera_id)
        except Exception as e:
            print("Failed to initialise driver:", e)
            return 1

        camera_backend = trifinger_cameras.camera.Backend(  # noqa: F841
            camera_driver, camera_data
        )

    camera_frontend = trifinger_cameras.camera.Frontend(camera_data)

    if args.record:
        logger = trifinger_cameras.camera.Logger(camera_data, 10000)
        logger.start()

    np.set_printoptions(precision=3, suppress=True)
    print("--- Camera Info: ----------------------")
    sinfo = camera_frontend.get_sensor_info()
    print(f"fps: {sinfo.frame_rate_fps}")
    print(f"width x height: {sinfo.image_width}x{sinfo.image_height}")
    print(sinfo.camera_matrix)
    print(sinfo.distortion_coefficients)
    print(sinfo.tf_world_to_camera)
    print("---------------------------------------")

    while True:
        observation = camera_frontend.get_latest_observation()
        image = utils.convert_image(observation.image)
        window_name = "Image Stream"
        cv2.imshow(window_name, image)

        # stop if either "q" or ESC is pressed
        if cv2.waitKey(3) in [ord("q"), 27]:  # 27 = ESC
            break

    if args.record:
        print("Save recorded data to file {}".format(args.record))
        logger.stop_and_save(args.record)

    return 0


if __name__ == "__main__":
    sys.exit(main())
