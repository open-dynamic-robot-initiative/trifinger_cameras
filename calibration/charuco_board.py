#!/usr/bin/env python3
"""Script for generating a Charuco Board, calibrating the camera with it
and detecting it in a live stream."""

import argparse
import os
import glob

import numpy as np
import cv2

# Based on the following tutorials:
# https://docs.opencv.org/3.4/df/d4a/tutorial_charuco_detection.html
# https://docs.opencv.org/3.4/da/d13/tutorial_aruco_calibration.html


class CharucoBoardHandler:

    def __init__(self):
        # use AprilTag 16h5 which contains 30 4x4 markers
        self.marker_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_APRILTAG_16h5)

        self.size_x = 5
        self.size_y = 7
        self.square_size = 0.04
        self.marker_size = 0.03

        self.board = cv2.aruco.CharucoBoard_create(self.size_x,
                                                   self.size_y,
                                                   self.square_size,
                                                   self.marker_size,
                                                   self.marker_dict)

        # Results of charuco calibration of one of the Basler cameras.
        self.camera_matrix = np.array([[589.60790224, 0., 366.49661804],
                                       [0., 590.17907342, 297.98736395],
                                       [0., 0., 1.]])
        self.dist_coeffs = np.array([[-0.24896938],
                                     [+0.13435385],
                                     [+0.00032044],
                                     [-0.00036141],
                                     [-0.06579839]])

    def create_board(self, filename, dpi=300):
        cm_per_inch = 2.54
        size = (int(self.size_x * self.square_size * 100 * dpi / cm_per_inch),
                int(self.size_y * self.square_size * 100 * dpi / cm_per_inch))
        img = self.board.draw(size)

        cv2.imwrite(filename, img)

    def detect_board(self, image):
        charuco_corners = None
        charuco_ids = None
        rvec = None
        tvec = None

        corners, ids, rejected = cv2.aruco.detectMarkers(image,
                                                         self.marker_dict)

        if ids is not None:
            num_corners, charuco_corners, charuco_ids = \
                cv2.aruco.interpolateCornersCharuco(
                    corners, ids, image, self.board,
                    cameraMatrix=self.camera_matrix,
                    distCoeffs=self.dist_coeffs)

            if charuco_ids is not None and self.camera_matrix is not None:
                valid, rvec, tvec = cv2.aruco.estimatePoseCharucoBoard(
                    charuco_corners, charuco_ids, self.board,
                    self.camera_matrix, self.dist_coeffs, None, None)
                if not valid:
                    rvec = None
                    tvec = None

        return charuco_corners, charuco_ids, rvec, tvec

    def visualize_board(self, image, charuco_corners, charuco_ids, rvec, tvec,
                        wait_key):
        debug_image = image

        if charuco_ids is not None:
            debug_image = cv2.aruco.drawDetectedCornersCharuco(
                image, charuco_corners)

            if rvec is not None and tvec is not None:
                debug_image = cv2.aruco.drawAxis(
                    debug_image, self.camera_matrix,
                    self.dist_coeffs, rvec, tvec, 0.1)

        # Display the resulting frame
        cv2.imshow('image', debug_image)
        if cv2.waitKey(wait_key) & 0xFF == ord('q'):
            return True
        else:
            return False

    def detect_board_and_visualize(self):
        cap = cv2.VideoCapture(0)
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()

            charuco_corners, charuco_ids, rvec, tvec = self.detect_board(frame)
            if self.visualize_board(frame, charuco_corners, charuco_ids, rvec,
                                    tvec, 1):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

    def detect_board_in_image(self, filename, visualize=False):
        assert filename is not None

        img = cv2.imread(filename)
        charuco_corners, charuco_ids, rvec, tvec = self.detect_board(img)
        if charuco_ids is None:
            print("No board detected")
        else:
            print("R: {}\nT: {}".format(rvec, tvec))
            if visualize:
                self.visualize_board(img, charuco_corners, charuco_ids,
                                     rvec, tvec, 0)

        return rvec, tvec

    def detect_boards_in_files(self, directory, file_pattern="*.jpeg",
                               visualize=False):
        all_corners = []
        all_ids = []

        pattern = os.path.join(directory, file_pattern)
        for filename in glob.glob(pattern):
            img = cv2.imread(filename)
            charuco_corners, charuco_ids, rvec, tvec = self.detect_board(img)
            if charuco_ids is not None:
                all_corners.append(charuco_corners)
                all_ids.append(charuco_ids)

                if visualize:
                    self.visualize_board(img, charuco_corners, charuco_ids,
                                         rvec, tvec, 1000)
            else:
                print("Board not detected in {}".format(filename))

        if visualize:
            cv2.destroyAllWindows()

        return all_corners, all_ids, img.shape[:2]

    def calibrate(self, calibration_data_directory, file_pattern="*.jpeg",
                  visualize=False):
        all_corners, all_ids, image_size = self.detect_boards_in_files(
            calibration_data_directory, file_pattern, visualize)

        camera_matrix = np.zeros((3, 3))
        dist_coeffs = np.zeros(4)
        error, camera_matrix, dist_coeffs, rvecs, tvecs = \
            cv2.aruco.calibrateCameraCharuco(all_corners, all_ids, self.board,
                                             image_size, camera_matrix,
                                             dist_coeffs)

        print("error: ", error)
        print("camera_matrix: ", camera_matrix)
        print("dist_coeffs: ", dist_coeffs)

        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs

        if visualize:
            # load the boards again to re-detect the boards with camera
            # calibration data
            self.detect_boards_in_files(
                calibration_data_directory, file_pattern, visualize)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["create_board",
                                           "detect_live",
                                           "detect_image",
                                           "calibrate"])
    parser.add_argument("--filename", type=str)
    parser.add_argument("--calibration-data", type=str)
    args = parser.parse_args()

    handler = CharucoBoardHandler()

    if args.action == "create_board":
        if not args.filename:
            raise RuntimeError("Filename not specified.")
        handler.create_board(args.filename)
    elif args.action == "detect_live":
        handler.detect_board_and_visualize()
    elif args.action == "detect_image":
        handler.detect_board_in_image(args.filename, visualize=True)
    elif args.action == "calibrate":
        handler.calibrate(args.calibration_data, visualize=True)


if __name__ == "__main__":
    main()
