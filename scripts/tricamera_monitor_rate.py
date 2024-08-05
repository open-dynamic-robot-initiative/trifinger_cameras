#!/usr/bin/env python3
"""Fetch tricamera observations in a loop and print the rate.

This is meant for easy testing of the actual frame rate.
"""

import argparse
import itertools
import json
import logging

import tqdm

import trifinger_cameras


def main() -> None:
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--store-timestamps",
        type=str,
        metavar="<filename>",
        help="""Store the timestamps from the observations of the three cameras
            into the specified json file.
        """,
    )
    argparser.add_argument(
        "--multi-process",
        action="store_true",
        help="""If set, use multiprocess camera data to access backend in other
            process.  Otherwise run the backend locally.
        """,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    args = argparser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(asctime)s] [%(name)s | %(levelname)s] %(message)s",
    )

    camera_names = ["camera60", "camera180", "camera300"]

    if args.multi_process:
        logging.debug("Start multi-process data")
        camera_data = trifinger_cameras.tricamera.MultiProcessData(
            "tricamera", False
        )
    else:
        logging.debug("Start single-process data")
        camera_data = trifinger_cameras.tricamera.SingleProcessData()
        logging.debug("Start back end")
        camera_driver = trifinger_cameras.tricamera.TriCameraDriver(
            *camera_names
        )
        camera_backend = trifinger_cameras.tricamera.Backend(  # noqa: F841
            camera_driver, camera_data
        )

    logging.debug("Start front end")
    camera_frontend = trifinger_cameras.tricamera.Frontend(camera_data)
    observations_timestamps_list = []

    # use tqdm to display the frame rate
    rate_monitor = tqdm.tqdm()
    logging.debug("Get start")
    t_start = camera_frontend.get_current_timeindex()
    logging.debug(f"Start at t = {t_start}")
    try:
        for t in itertools.count(start=t_start):
            rate_monitor.update()
            observation = camera_frontend.get_observation(t)

            observations_timestamps_list.append(
                [
                    observation.cameras[0].timestamp,
                    observation.cameras[1].timestamp,
                    observation.cameras[2].timestamp,
                ]
            )

    except Exception as e:
        logging.error(e)

    rate_monitor.close()

    if args.store_timestamps:
        with open(args.store_timestamps, "w") as f:
            json.dump(observations_timestamps_list, f)


if __name__ == "__main__":
    main()
