#!/usr/bin/env python3
"""Run back-end for a single camera, using multi-process robot data."""

import argparse
import logging
import sys
import time

import signal_handler
import trifinger_cameras


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pylon",
        action="store_true",
        help="""Access the camera via Pylon.  If not set, OpenCV is used.""",
    )
    parser.add_argument(
        "--camera-id",
        "-c",
        default="",
        help="""ID of the camera that is used.  If --pylon is set this refers
            to the DeviceUserId, otherwise it is the index of the device.
        """,
    )
    args = parser.parse_args()

    # === configure logging

    log_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        format="[%(levelname)s %(asctime)s] %(message)s",
        level=logging.DEBUG,
        handlers=[log_handler],
    )

    return args


def main() -> int:
    args = parse_arguments()

    try:
        if args.pylon:
            camera_driver = trifinger_cameras.camera.PylonDriver(args.camera_id)
        else:
            camera_id = int(args.camera_id) if args.camera_id else 0
            camera_driver = trifinger_cameras.camera.OpenCVDriver(camera_id)
    except Exception as e:
        logging.error("Failed to initialise driver: %s", e)
        return 1

    logging.info("Start camera backend")

    CAMERA_TIME_SERIES_LENGTH = 1000
    camera_data = trifinger_cameras.camera.MultiProcessData(
        "camera", True, CAMERA_TIME_SERIES_LENGTH
    )
    camera_backend = trifinger_cameras.camera.Backend(camera_driver, camera_data)

    logging.info("Camera backend ready.")

    signal_handler.init()
    while not signal_handler.has_received_sigint():
        time.sleep(1)

    camera_backend.shutdown()

    return 0


if __name__ == "__main__":
    returncode = main()
    sys.exit(returncode)
