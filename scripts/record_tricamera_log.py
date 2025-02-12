#!/usr/bin/env python3
"""Run the TriCamera backend and logger to record data."""

import argparse
import logging
import pathlib
import sys
import time

import signal_handler
import trifinger_cameras


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_path",
        type=pathlib.Path,
        help="File to which the camera data is written.",
    )
    parser.add_argument(
        "--buffer-size",
        "-b",
        type=int,
        default=60,
        help="Buffer size of the logger in seconds. Default: %(default)s",
    )
    parser.add_argument(
        "--no-downsample",
        action="store_true",
        help="Disable downsampling in the camera driver",
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing files."
    )
    parser.add_argument(
        "--multi-process",
        action="store_true",
        help="""If set, use multiprocess camera data to access backend in other
            process.  Otherwise run the backend locally.
        """,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(asctime)s] [%(name)s | %(levelname)s] %(message)s",
    )

    camera_names = ["camera60", "camera180", "camera300"]

    if not args.force and args.output_path.exists():
        logging.fatal("%s already exists.  Use --force to overwrite", args.output_path)
        return 1

    if args.multi_process:
        camera_data = trifinger_cameras.tricamera.MultiProcessData("tricamera", False)
    else:
        downsample = not args.no_downsample
        camera_data = trifinger_cameras.tricamera.SingleProcessData()
        camera_driver = trifinger_cameras.tricamera.TriCameraDriver(
            *camera_names, downsample
        )
        camera_backend = trifinger_cameras.tricamera.Backend(camera_driver, camera_data)

    camera_frontend = trifinger_cameras.tricamera.Frontend(camera_data)
    camera_info = camera_frontend.get_sensor_info()

    log_size = int(camera_info.camera[0].frame_rate_fps * args.buffer_size)

    camera_logger = trifinger_cameras.tricamera.Logger(camera_data, log_size)
    camera_logger.start()
    logging.info("Start camera logging.  Press Ctrl+C to stop and save.")

    signal_handler.init()
    while not signal_handler.has_received_sigint():
        time.sleep(1)

    logging.info("Save recorded camera data to file %s", args.output_path)
    camera_logger.stop_and_save(str(args.output_path))

    camera_backend.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())
