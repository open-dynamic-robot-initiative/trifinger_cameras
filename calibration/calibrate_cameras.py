#!/usr/bin/env python3
"""Script for generating the calibration data for the cameras and verifying the output.
"""

from charuco_board import CharucoBoardHandler
import argparse
import numpy as np
import json
from utils import NumpyEncoder
import matplotlib.pyplot as plt
import cv2
import codecs


def calibrate_intrinsic_parameters(handler, calibration_data, calibration_results_file):
    camera_matrix, dist_coeffs, error = handler.calibrate(calibration_data, visualize=True)
    calibration_results = dict()
    calibration_results['camera_matrix'] = camera_matrix
    calibration_results['dist_coeffs'] = dist_coeffs
    calibration_results['error'] = error

    with open(calibration_results_file, 'w') as outfile:
        json.dump(calibration_results, outfile, cls=NumpyEncoder)
    return


def calibrate_extrinsic_parameters(handler,calibration_results_file,  churoco_centralized_image_filename,
                                   extrinsic_calibration_filename, impose_cube=True):
    rvec, tvec = handler.detect_board_in_image(churoco_centralized_image_filename, visualize=False)
    calibration_results = dict()
    calibration_results['R'] = rvec
    calibration_results['T'] = tvec
    with open(extrinsic_calibration_filename, 'w') as outfile:
        json.dump(calibration_results, outfile, cls=NumpyEncoder)

    if impose_cube:
        new_object_points = np.array([[0, 0, 0],
                                      [0, 1, 0],
                                      [1, 0, 0],
                                      [1, 1, 0],
                                      [0, 0, 1],
                                      [0, 1, 1],
                                      [1, 0, 1],
                                      [1, 1, 1],
                                      ], dtype=np.float32) * 0.04
        img = cv2.imread(churoco_centralized_image_filename)
        calibration_results_text = codecs.open(calibration_results_file, 'r', encoding='utf-8').read()
        calibration_data = json.loads(calibration_results_text)
        imgpoints, _ = cv2.projectPoints(new_object_points, rvec, tvec, np.array(calibration_data['camera_matrix']),
                                         np.array(calibration_data['dist_coeffs']))
        plt.plot([imgpoints[0, 0, 0], imgpoints[4, 0, 0]], [imgpoints[0, 0, 1], imgpoints[4, 0, 1]])
        plt.plot([imgpoints[1, 0, 0], imgpoints[5, 0, 0]], [imgpoints[1, 0, 1], imgpoints[5, 0, 1]])
        plt.plot([imgpoints[2, 0, 0], imgpoints[6, 0, 0]], [imgpoints[2, 0, 1], imgpoints[6, 0, 1]])
        plt.plot([imgpoints[3, 0, 0], imgpoints[7, 0, 0]], [imgpoints[3, 0, 1], imgpoints[7, 0, 1]])
        plt.plot([imgpoints[0, 0, 0], imgpoints[1, 0, 0]], [imgpoints[0, 0, 1], imgpoints[1, 0, 1]])
        plt.plot([imgpoints[0, 0, 0], imgpoints[2, 0, 0]], [imgpoints[0, 0, 1], imgpoints[2, 0, 1]])
        plt.plot([imgpoints[1, 0, 0], imgpoints[3, 0, 0]], [imgpoints[1, 0, 1], imgpoints[3, 0, 1]])
        plt.plot([imgpoints[2, 0, 0], imgpoints[3, 0, 0]], [imgpoints[2, 0, 1], imgpoints[3, 0, 1]])
        plt.plot([imgpoints[4, 0, 0], imgpoints[5, 0, 0]], [imgpoints[4, 0, 1], imgpoints[5, 0, 1]])
        plt.plot([imgpoints[4, 0, 0], imgpoints[6, 0, 0]], [imgpoints[4, 0, 1], imgpoints[6, 0, 1]])
        plt.plot([imgpoints[5, 0, 0], imgpoints[7, 0, 0]], [imgpoints[5, 0, 1], imgpoints[7, 0, 1]])
        plt.plot([imgpoints[6, 0, 0], imgpoints[7, 0, 0]], [imgpoints[6, 0, 1], imgpoints[7, 0, 1]])
        plt.scatter(imgpoints[:, 0, 0], imgpoints[:, 0, 1], color='r', marker='x', s=5)
        plt.imshow(img)
        plt.show()
        return


def main():
    """Execute an action depending on arguments passed by the user."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["intrinsic_calibration",
                                           "extrinsic_calibration"],
                        help="""Action that is executed.""")

    parser.add_argument("--intrinsic_calibration_filename", type=str,
                        help="""Filename used for saving intrinsic calibration data or loading it
                        """)

    parser.add_argument("--calibration-data", type=str,
                        help="""Path to the calibration data directory (only
                        used for action 'intrinsic_calibration').
                        """)

    parser.add_argument("--extrinsic_calibration_filename", type=str,
                        help="""Filename used for saving intrinsic calibration data.
                            """)
    parser.add_argument("--image_view_filename", type=str,
                        help="""Image with chruco centralized at the (0, 0, 0) position.
                                """)

    args = parser.parse_args()
    handler = CharucoBoardHandler()

    if args.action == "intrinsic_calibration":
        if not args.intrinsic_calibration_filename:
            raise RuntimeError("intrinsic_calibration_filename not specified.")
        if not args.calibration_data:
            raise RuntimeError("calibration_data not specified.")
        calibrate_intrinsic_parameters(handler, args.calibration_data, args.intrinsic_calibration_filename)
    elif args.action == "extrinsic_calibration":
        if not args.intrinsic_calibration_filename:
            raise RuntimeError("intrinsic_calibration_filename not specified.")
        if not args.extrinsic_calibration_filename:
            raise RuntimeError("extrinsic_calibration_filename not specified.")
        if not args.image_view_filename:
            raise RuntimeError("image_view_filename not specified.")
        calibrate_extrinsic_parameters(handler, args.intrinsic_calibration_filename, args.image_view_filename,
                                       args.extrinsic_calibration_filename, impose_cube=True)

if __name__ == "__main__":
    main()
