#!/usr/bin/env python3
"""Run back-end for the tricamera setup, using multi-process data."""

import argparse
import logging
import pathlib
import sys
import time

import signal_handler
import trifinger_cameras


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "parameter_file_camera60",
        type=pathlib.Path,
        help="Parameter file for camera60.",
    )
    parser.add_argument(
        "parameter_file_camera180",
        type=pathlib.Path,
        help="Parameter file for camera180.",
    )
    parser.add_argument(
        "parameter_file_camera300",
        type=pathlib.Path,
        help="Parameter file for camera180.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    args = parser.parse_args()

    # === configure logging

    log_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        format="[%(levelname)s %(asctime)s] %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
        handlers=[log_handler],
    )

    return args


def main() -> int:
    args = parse_arguments()

    try:
        camera_driver = trifinger_cameras.tricamera.TriCameraDriver(
            args.parameter_file_camera60,
            args.parameter_file_camera180,
            args.parameter_file_camera300,
        )
    except Exception as e:
        logging.error("Failed to initialise driver: %s", e)
        return 1

    logging.info("Start camera backend")

    CAMERA_TIME_SERIES_LENGTH = 100
    camera_data = trifinger_cameras.tricamera.MultiProcessData(
        "tricamera", True, CAMERA_TIME_SERIES_LENGTH
    )
    camera_backend = trifinger_cameras.tricamera.Backend(camera_driver, camera_data)

    logging.info("Camera backend ready.")

    signal_handler.init()
    while not signal_handler.has_received_sigint():
        time.sleep(1)

    camera_backend.shutdown()

    return 0


if __name__ == "__main__":
    returncode = main()
    sys.exit(returncode)
