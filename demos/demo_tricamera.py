#!/usr/bin/env python3
"""
This demo is to start three pylon dependent cameras, view their image streams,
and if desired, store the timestamps from them to analyse how well the three
cameras are in sync with each other.
"""

import argparse
import pickle

import cv2
import numpy as np

import trifinger_cameras
from trifinger_cameras import utils


def main() -> None:  # noqa: D103
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--store-timestamps",
        type=str,
        metavar="FILENAME",
        help="""Store the timestamps from the observations of the three cameras
            into the specified pickle file.
        """,
    )
    argparser.add_argument(
        "--multi-process",
        action="store_true",
        help="""If set, use multiprocess camera data to access backend in other
            process.  Otherwise run the backend locally.
        """,
    )
    args = argparser.parse_args()

    camera_names = ["camera60", "camera180", "camera300"]

    if args.multi_process:
        camera_data = trifinger_cameras.tricamera.MultiProcessData("tricamera", False)
    else:
        camera_data = trifinger_cameras.tricamera.SingleProcessData()
        camera_driver = trifinger_cameras.tricamera.TriCameraDriver(*camera_names)
        camera_backend = trifinger_cameras.tricamera.Backend(  # noqa: F841
            camera_driver, camera_data
        )

    camera_frontend = trifinger_cameras.tricamera.Frontend(camera_data)
    observations_timestamps_list = []

    np.set_printoptions(precision=3, suppress=True)
    print("=== Camera Info: ======================")
    for i, info in enumerate(camera_frontend.get_sensor_info().camera):
        print(f"--- Camera {i}: ----------------------")
        print(f"fps: {info.frame_rate_fps}")
        print(f"width x height: {info.image_width}x{info.image_height}")
        print(info.camera_matrix)
        print(info.distortion_coefficients)
        print(info.tf_world_to_camera)
        print("---------------------------------------")
    print("=======================================")

    while True:
        observation = camera_frontend.get_latest_observation()
        for i, name in enumerate(camera_names):
            cv2.imshow(name, utils.convert_image(observation.cameras[i].image))

        # stop if either "q" or ESC is pressed
        if cv2.waitKey(3) in [ord("q"), 27]:  # 27 = ESC
            break

        observations_timestamps_list.append(
            [
                observation.cameras[0].timestamp,
                observation.cameras[1].timestamp,
                observation.cameras[2].timestamp,
            ]
        )

    if args.store_timestamps:
        with open(args.store_timestamps, "wb") as f:
            pickle.dump(observations_timestamps_list, f)


if __name__ == "__main__":
    main()
