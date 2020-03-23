#!/usr/bin/env python3
"""Script for generating a Charuco Board, calibrating the camera with it and
detecting it in images and camera streams.
"""
import argparse

from trifinger_cameras.charuco_board_handler import CharucoBoardHandler


def main():
    """Execute an action depending on arguments passed by the user."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create_board",
                                           "detect_live",
                                           "detect_image",
                                           "calibrate"],
                        help="""Action that is executed.""")
    parser.add_argument("--filename", type=str,
                        help="""Filename used for saving or loading images
                        (depending on the action).
                        """)
    parser.add_argument("--calibration-data", type=str,
                        help="""Path to the calibration data directory (only
                        used for action 'calibrate').
                        """)
    parser.add_argument("--no-gui", action="store_true",
                        help="""Set to disable any GUI-based visualization.""")
    args = parser.parse_args()

    handler = CharucoBoardHandler()

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
        handler.calibrate(args.calibration_data, visualize=not args.no_gui)


if __name__ == "__main__":
    main()
