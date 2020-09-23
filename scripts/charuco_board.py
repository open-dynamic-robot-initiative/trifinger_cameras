#!/usr/bin/env python3
"""Script for generating a Charuco Board, calibrating the camera with it and
detecting it in images and camera streams.
"""
import os
import glob
import argparse

from trifinger_cameras.charuco_board_handler import CharucoBoardHandler
from trifinger_cameras.camera_calibration_file import CameraCalibrationFile


BOARD_SIZE_X = 5
BOARD_SIZE_Y = 10
BOARD_SQUARE_SIZE = 0.04
BOARD_MARKER_SIZE = 0.03


def main():
    """Execute an action depending on arguments passed by the user."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["create_board", "detect_live", "detect_image", "calibrate"],
        help="""Action that is executed.""",
    )
    parser.add_argument(
        "--filename",
        type=str,
        help="""Filename used for saving or loading images (depending on the
            action).
        """,
    )
    parser.add_argument(
        "--calibration-data",
        type=str,
        help="""Path to the calibration data directory (only used for action
            'calibrate').
        """,
    )
    parser.add_argument(
        "--camera-info",
        type=str,
        help="""Camera info file, including intrinsic parameters.""",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="""Set to disable any GUI-based visualization.""",
    )
    args = parser.parse_args()

    camera_matrix = None
    distortion_coeffs = None
    if args.camera_info:
        camera_info = CameraCalibrationFile(args.camera_info)
        camera_matrix = camera_info["camera_matrix"]
        distortion_coeffs = camera_info["distortion_coefficients"]

    handler = CharucoBoardHandler(
        BOARD_SIZE_X,
        BOARD_SIZE_Y,
        BOARD_SQUARE_SIZE,
        BOARD_MARKER_SIZE,
        camera_matrix,
        distortion_coeffs,
    )

    if args.action == "create_board":
        if not args.filename:
            raise RuntimeError("Filename not specified.")
        handler.save_board(args.filename)
    elif args.action == "detect_live":
        handler.detect_board_in_camera_stream()
    elif args.action == "detect_image":
        if not args.filename:
            raise RuntimeError("Filename not specified.")
        handler.detect_board_in_image(args.filename, visualize=not args.no_gui)
    elif args.action == "calibrate":
        pattern = os.path.join(args.calibration_data, args.filename)
        files = glob.glob(pattern)
        handler.calibrate(
            files,
            visualize=not args.no_gui,
        )


if __name__ == "__main__":
    main()
