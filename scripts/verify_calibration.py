#!/usr/bin/env python3
"""Verify calibration by re-projecting points from the calibration board.

This is supposed to be used with an image of the calibration board.  The board
contains several markers at known positions.  This script re-projects these
points to the image and marks them there.  For good camera calibration the
marked points in the image should match with the positions of the markers that
are visible on the calibration board.
"""
import argparse

import cv2
import numpy as np

from trifinger_cameras.charuco_board_handler import CharucoBoardHandler
from trifinger_cameras.camera_calibration_file import CameraCalibrationFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        type=str,
        required=True,
        help="""Path to the image in which the points are visualized.""",
    )
    parser.add_argument(
        "-c",
        type=str,
        required=True,
        help="""Path to the camera calibration file.""",
    )
    parser.add_argument(
        "--detect-board-position",
        action="store_true",
        help="""Detect the board position from the image instead of using the
            pose from the calibration file.""",
    )
    args = parser.parse_args()

    camera_info = CameraCalibrationFile(args.c)
    camera_matrix = camera_info["camera_matrix"]
    distortion_coeffs = camera_info["distortion_coefficients"]
    handler = CharucoBoardHandler(camera_matrix, distortion_coeffs)

    points = np.vstack(
        [
            x.flatten()
            for x in np.meshgrid(
                np.arange(-0.3, 0.4, 0.1), np.arange(-0.3, 0.4, 0.1), [0.0],
            )
        ]
    ).T

    image = cv2.imread(args.i)

    if args.detect_board_position:
        _, _, rvec, tvec = handler.detect_board(image)

        board_offset = np.array([0.1, 0.14, 0])
        points = points + board_offset
    else:
        # get rvec and tvec from projection matrix
        pose_mat = camera_info["projection_matrix"]
        tvec = pose_mat[0:3, 3]
        rvec = cv2.Rodrigues(pose_mat[:3, :3])[0]

    imgpoints, _ = cv2.projectPoints(
        points, rvec, tvec, camera_matrix, distortion_coeffs,
    )

    for imgpoint in imgpoints:
        cv2.drawMarker(
            image, tuple(imgpoint[0].astype(int)), tuple([0, 0, 255])
        )

    cv2.imshow("foo", image)
    cv2.waitKey()


if __name__ == "__main__":
    main()
