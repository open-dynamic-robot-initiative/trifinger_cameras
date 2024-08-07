"""Class for Charuco board detection and camera calibration."""

import glob
import json
import os
import pickle
import typing

import numpy as np

# annoying hack to get the proper version of cv2 (_not_ the ROS one)
import sys

ros_path = "/opt/ros/kinetic/lib/python2.7/dist-packages"
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2

sys.path.append(ros_path)


# Based on the following tutorials:
# https://docs.opencv.org/4.2.0/df/d4a/tutorial_charuco_detection.html
# https://docs.opencv.org/4.2.0/da/d13/tutorial_aruco_calibration.html


class CharucoBoardHandler:
    """Provides different actions using a Charuco Board."""

    def __init__(
        self,
        size_x: int,
        size_y: int,
        square_size: float,
        marker_size: float,
        camera_matrix=None,
        dist_coeffs=None,
    ):
        """Initialize board with hard-coded parameters."""
        # use AprilTag 16h5 which contains 30 4x4 markers
        self.marker_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_APRILTAG_16h5
        )

        self.size_x = size_x
        self.size_y = size_y
        self.square_size = square_size
        self.marker_size = marker_size

        self.board = cv2.aruco.CharucoBoard_create(
            self.size_x,
            self.size_y,
            self.square_size,
            self.marker_size,
            self.marker_dict,
        )

        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs

    def save_board(self, filename, dpi=300):
        """Save the board as image.

        Args:
            filename (str): Output filename.
            dpi (int): Dots per inch.  Used to determine the pixel size of the
                image based on the size of the squares.  Note that OpenCV does
                not store the dpi value itself in the image file.
        """
        cm_per_inch = 2.54
        size = (
            int(self.size_x * self.square_size * 100 * dpi / cm_per_inch),
            int(self.size_y * self.square_size * 100 * dpi / cm_per_inch),
        )
        img = self.board.draw(size)

        cv2.imwrite(filename, img)

    def detect_board(self, image):
        """Detect the board in the given image.

        Args:
            image: Intput image.

        Returns:
            (tuple): Tuple containing:

                charuco_corners: Pixel-positions of the detected corners.
                charuco_ids: IDs of the detected corners.
                rvec: Orientation of the board given as a Rodrigues vector.
                    Only if camera matrix is set.
                tvec: Translation of the board.  Only if camera matrix is set.
        """
        charuco_corners = None
        charuco_ids = None
        rvec = None
        tvec = None

        # disable corner refinement of marker detection as recommended in
        # https://docs.opencv.org/4.2.0/df/d4a/tutorial_charuco_detection.html
        params = cv2.aruco.DetectorParameters_create()
        params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_NONE

        corners, ids, rejected = cv2.aruco.detectMarkers(
            image, self.marker_dict, parameters=params
        )

        if ids is not None:
            (
                num_corners,
                charuco_corners,
                charuco_ids,
            ) = cv2.aruco.interpolateCornersCharuco(
                corners,
                ids,
                image,
                self.board,
                cameraMatrix=self.camera_matrix,
                distCoeffs=self.dist_coeffs,
            )

            if charuco_ids is not None and self.camera_matrix is not None:
                valid, rvec, tvec = cv2.aruco.estimatePoseCharucoBoard(
                    charuco_corners,
                    charuco_ids,
                    self.board,
                    self.camera_matrix,
                    self.dist_coeffs,
                    None,
                    None,
                )
                if not valid:
                    rvec = None
                    tvec = None

        return charuco_corners, charuco_ids, rvec, tvec

    def visualize_board(
        self, image, charuco_corners, charuco_ids, rvec, tvec, wait_key
    ):
        """Visualize a detected board in the image.

        Visualizes the detected board (corners and pose if given) in the image
        and shows it using `cv2.imshow`.

        Args:
            image:  Image in which the board was detected.
            charuco_corners:  See return value of `detect_board()`.
            charuco_ids:  See return value of `detect_board()`.
            rvec:  See return value of `detect_board()`.
            tvec:  See return value of `detect_board()`.
            wait_key:  Value that is passed to `cv2.waitKey()` when showing the
                image.

        Returns:
            (bool):  True if the User pressed "q" in the image window,
                otherwise False.
        """
        debug_image = image

        if charuco_ids is not None:
            debug_image = cv2.aruco.drawDetectedCornersCharuco(image, charuco_corners)

            if rvec is not None and tvec is not None:
                debug_image = cv2.aruco.drawAxis(
                    debug_image,
                    self.camera_matrix,
                    self.dist_coeffs,
                    rvec,
                    tvec,
                    0.1,
                )

        # Display the resulting frame
        cv2.imshow("image", debug_image)
        if cv2.waitKey(wait_key) & 0xFF == ord("q"):
            return True
        else:
            return False

    def detect_board_in_camera_stream(self, device=0):
        """Show images from a camera and visualize the board if it is detected.

        The function will loop forever.  Press "q" in the image window to stop.

        Args:
            device (int): ID of the video capture device (e.g. a webcam).
        """
        cap = cv2.VideoCapture(device)
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            charuco_corners, charuco_ids, rvec, tvec = self.detect_board(frame)
            if self.visualize_board(frame, charuco_corners, charuco_ids, rvec, tvec, 1):
                break

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

    def detect_board_in_image(self, filename, visualize=False):
        """Detect the board in the given image.

        Returns the pose of the board if it is detected and also prints these
        values to stdout.

        Args:
            filename (str):  Path to the image file.
            visualize (bool):  If True, the result is visualized (press "q" to
                close the image window).

        Returns:
            (tuple): Tuple containing

                - rvec: Orientation of the board as a Rodrigues vector.
                - tvec: Translation of the board.

            Values are None if the board is not detected.
        """
        assert filename is not None

        # load file depending on extension (pickle or image)
        _, extension = os.path.splitext(filename)
        if extension == ".pickle":
            with open(filename, "rb") as file_handle:
                img = pickle.load(file_handle, encoding="latin1")
        else:
            img = cv2.imread(filename)

        charuco_corners, charuco_ids, rvec, tvec = self.detect_board(img)
        if charuco_ids is not None:
            if visualize:
                self.visualize_board(img, charuco_corners, charuco_ids, rvec, tvec, 0)

        if rvec is not None:
            print(json.dumps({"rvec": rvec.tolist(), "tvec": tvec.tolist()}))
        else:
            print(json.dumps({"rvec": None, "tvec": None}))

        return rvec, tvec

    def detect_board_in_files(self, files: typing.List[str], visualize: bool = False):
        """Detect the board in multiple files.

        Tries to detect the Charuco board in the given list of image files.

        Args:
            files:  List of paths to image files.
            visualize (bool):  If True, each image is shown for one second,
                visualizing the board if it is detected.

        Returns:
            tuple: Tuple containing

                - all_corners:  List of lists of pixel-positions of detected
                      charuco corners (one element per image).
                - all_ids:  List of lists of IDs of detected charuco corners
                      (one element per image).
                - image_shape:  Tuple with width and height of the images
                      (assumes all images have same size!)
        """
        all_corners = []
        all_ids = []

        for filename in files:
            img = cv2.imread(filename)
            charuco_corners, charuco_ids, rvec, tvec = self.detect_board(img)
            if charuco_ids is not None:
                all_corners.append(charuco_corners)
                all_ids.append(charuco_ids)

                if visualize:
                    self.visualize_board(
                        img, charuco_corners, charuco_ids, rvec, tvec, 1000
                    )
            else:
                print("Board not detected in {}".format(filename))

        if visualize:
            cv2.destroyAllWindows()

        return all_corners, all_ids, img.shape[:2]

    def calibrate(
        self,
        files: typing.List[str],
        visualize: bool = False,
    ):
        """Calibrate camera given a directory of images.

        Loads the given images and uses them for Charuco-based camera
        calibration.
        The resulting coefficients are printed to stdout and stored internally
        so they are used when detecting boards later on.

        Args:
            files (list):  List of image files.
            visualize (bool):  If True, visualize the detected corners when
                loading the images and visualize again after the calibration
                including the pose of the board.
        """
        # clear old calibration data
        self.camera_matrix = None
        self.dist_coeffs = None

        all_corners, all_ids, image_size = self.detect_board_in_files(files, visualize)

        camera_matrix = np.zeros((3, 3))
        dist_coeffs = np.zeros(4)
        (
            error,
            camera_matrix,
            dist_coeffs,
            rvecs,
            tvecs,
        ) = cv2.aruco.calibrateCameraCharuco(
            all_corners,
            all_ids,
            self.board,
            image_size,
            camera_matrix,
            dist_coeffs,
        )

        print("error: ", error)
        print("camera_matrix: ", camera_matrix)
        print("dist_coeffs: ", dist_coeffs)

        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs

        if visualize:
            # load the boards again to re-detect the boards with camera
            # calibration data
            self.detect_board_in_files(files, visualize)
        return camera_matrix, dist_coeffs, error
