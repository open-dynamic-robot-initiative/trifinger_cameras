#!/usr/bin/env python3
"""
This demo is to start three pylon dependent cameras, view their image streams,
and if desired, store the timestamps from them to analyse how well the three
cameras are in sync with each other.
"""
import argparse
import cv2
import pickle

import trifinger_cameras
from trifinger_cameras import utils


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--store-timestamps",
        type=str,
        help="""Pass --store_timestamps to dump the timestamps from the observations
             of the three cameras into a pickle file, followed by the name of
             this pickle file (for eg. time_stamps.p).
             """,
    )
    args = argparser.parse_args()

    camera_data = trifinger_cameras.tricamera.SingleProcessData()
    camera_driver = trifinger_cameras.tricamera.TriCameraDriver(
        "camera60", "camera180", "camera300"
    )

    camera_backend = trifinger_cameras.tricamera.Backend(  # noqa
        camera_driver, camera_data
    )
    camera_frontend = trifinger_cameras.tricamera.Frontend(camera_data)
    observations_timestamps_list = []

    while True:
        observation = camera_frontend.get_latest_observation()
        window_60 = "Image Stream camera60"
        window_180 = "Image Stream camera180"
        window_300 = "Image Stream camera300"
        cv2.imshow(
            window_180, utils.convert_image(observation.cameras[0].image)
        )
        cv2.imshow(
            window_300, utils.convert_image(observation.cameras[1].image)
        )
        cv2.imshow(
            window_60, utils.convert_image(observation.cameras[2].image)
        )

        # stop if either "q" or ESC is pressed
        if cv2.waitKey(3) in [ord("q"), 27]:  # 27 = ESC
            break

        observations_timestamps_list.append(
            [
                observation.cameras[0].time_stamp,
                observation.cameras[1].time_stamp,
                observation.cameras[2].time_stamp,
            ]
        )

    if args.store_timestamps:
        pickle.dump(
            observations_timestamps_list, open(args.store_timestamps, "wb")
        )


if __name__ == "__main__":
    main()
