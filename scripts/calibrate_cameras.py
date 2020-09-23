#!/usr/bin/env python3
"""Script for generating the calibration data for the cameras and verifying the
 output.
"""

from trifinger_cameras.charuco_board_handler import CharucoBoardHandler
import trifinger_cameras.utils as utils
import argparse
import numpy as np
import cv2
import yaml

import json
import os
import glob

from IPython import embed


def calibrate_intrinsic_parameters(calibration_data, calibration_results_file):
    """Calibrate intrinsic parameters of the camera given different images
    taken for the Charuco board from different views, the resulting parameters
    are saved to the provided filename.

    Args:
        calibration_data (str):  directory of the stored images of the
        Charuco board.
        calibration_results_file (str):  filepath that will be used to write
        the calibration results in.
    """
    handler = CharucoBoardHandler()

    camera_matrix, dist_coeffs, error = handler.calibrate(
        calibration_data, visualize=True
    )
    camera_info = dict()
    camera_info["camera_matrix"] = dict()
    camera_info["camera_matrix"]["rows"] = 3
    camera_info["camera_matrix"]["cols"] = 3
    camera_info["camera_matrix"]["data"] = camera_matrix.flatten().tolist()
    camera_info["distortion_coefficients"] = dict()
    camera_info["distortion_coefficients"]["rows"] = 1
    camera_info["distortion_coefficients"]["cols"] = 5
    camera_info["distortion_coefficients"][
        "data"
    ] = dist_coeffs.flatten().tolist()

    with open(calibration_results_file, "w") as outfile:
        yaml.dump(
            camera_info,
            outfile,
            default_flow_style=False,
        )
    return camera_matrix, dist_coeffs


def calibrate_extrinsic_parameters(
    calibration_results_file,
    charuco_centralized_image_filename,
    extrinsic_calibration_filename,
    impose_cube=True,
):
    """Calibrate extrinsic parameters of the camera given one image taken for
    the Charuco board centered at (0, 0, 0) the resulting parameters are
    saved to the provided filename and a virtual cube is imposed on the
    board for verification.

    Args:
        calibration_results_file (str):  filepath that will be used to read
        the intrinsic calibration results.
        charuco_centralized_image_filename (str): filename of the image
        taken for the Charuco board centered at (0, 0, 0).
        extrinsic_calibration_filename (str):  filepath that will be used
        to write the extrinsic calibration results in.
        impose_cube (bool): boolean whether to output a virtual cube
        imposed on the first square of the board or not.
    """
    with open(calibration_results_file) as file:
        calibration_data = yaml.safe_load(file)

    def config_matrix(data):
        return np.array(data["data"]).reshape(data["rows"], data["cols"])

    camera_matrix = config_matrix(calibration_data["camera_matrix"])
    dist_coeffs = config_matrix(calibration_data["distortion_coefficients"])

    handler = CharucoBoardHandler(camera_matrix, dist_coeffs)

    rvec, tvec = handler.detect_board_in_image(
        charuco_centralized_image_filename, visualize=False
    )

    # projection_matrix = np.zeros((4, 4))
    projection_matrix = utils.rodrigues_to_matrix(rvec)
    projection_matrix[0:3, 3] = tvec[:, 0]
    projection_matrix[3, 3] = 1

    calibration_data["projection_matrix"] = dict()
    calibration_data["projection_matrix"]["rows"] = 4
    calibration_data["projection_matrix"]["cols"] = 4
    calibration_data["projection_matrix"][
        "data"
    ] = projection_matrix.flatten().tolist()

    with open(extrinsic_calibration_filename, "w") as outfile:
        yaml.dump(
            calibration_data,
            outfile,
            default_flow_style=False,
        )

    if impose_cube:
        new_object_points = (
            np.array(
                [
                    [0, 0, 0],
                    [0, 1, 0],
                    [1, 0, 0],
                    [1, 1, 0],
                    [0, 0, 1],
                    [0, 1, 1],
                    [1, 0, 1],
                    [1, 1, 1],
                ],
                dtype=np.float32,
            )
            * 0.04
        )

        world_origin_points = (
            np.array(
                [
                    [0, 0, 0],
                    [0, 1, 0],
                    [1, 0, 0],
                    [0, 0, 1],
                ],
                dtype=np.float32,
            )
            * 0.1
        )

        # cube
        point_pairs = (
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
            (4, 5),
            (4, 6),
            (5, 7),
            (6, 7),
        )

        img = cv2.imread(charuco_centralized_image_filename)
        imgpoints, _ = cv2.projectPoints(
            new_object_points,
            rvec,
            tvec,
            camera_matrix,
            dist_coeffs,
        )

        for p1, p2 in point_pairs:
            cv2.line(
                img,
                tuple(imgpoints[p1, 0]),
                tuple(imgpoints[p2, 0]),
                [200, 200, 0],
                thickness=2,
            )

        cv2.imshow("Imposed Cube", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def calibrate_mean_extrinsic_parameters(
    camera_matrix,
    dist_coeffs,
    charuco_centralized_image_dir,
    extrinsic_calibration_filename,
    impose_cube=True,
):
    """Calibrate extrinsic parameters of the camera given several imaeges taken for
    the Charuco board centered at (0, 0, 0). transform the extrinsic parameters into the
    fixed 'world' coordinate system.
    the resulting parameters are averaged for all images and saved to the provided filename.
    a virtual cube on the board as well as the world coordinates axes are imposed for verification.

    Args:
        camera_matrix, dist_coeffs:  output of the intrinsic calibration (either read from file or directly obtained from
        intrinsic calibration function.
        charuco_centralized_image_dir (str): directory containing images
        taken for the Charuco board centered at (0, 0, 0).
        extrinsic_calibration_filename (str):  filepath that will be used
        to write the extrinsic calibration results in.
        impose_cube (bool): boolean whether to output a virtual cube
        imposed on the first square of the board or not.
    """

    handler = CharucoBoardHandler(camera_matrix, dist_coeffs)

    file_pattern = "*.png"
    pattern = os.path.join(charuco_centralized_image_dir, file_pattern)

    ind = 0
    projection_matrix = np.zeros((len(glob.glob(pattern)), 4, 4))

    for filename in glob.glob(pattern):
        img = cv2.imread(filename)

        rvec, tvec = handler.detect_board_in_image(filename, visualize=False)

        # geometric data of the calibration board with respect to the 'world' coordinates

        # inclination angle of the board (CAD data)
        alpha = 22
        alphr = np.radians(alpha)
        # half-width of the calibration board (CAD data)
        Dx = 0.105
        # projected (on the base) half-height of the calibration board (CAD data)
        Dy = 0.16054

        # thickness of the base-plate (measured)
        T1 = 0.00435
        # thickness of the calibration board plate (measured)
        T2 = 0.0045
        # y-distance of the pattern axis from the plate edge (measured)
        dy = 0.0378
        # x-distance of the pattern axis from the plate edge (measured)
        dx = 0.0047

        # x-distance of the pattern origin to the world origin
        tx = Dx - dx
        # y-distance of the pattern origin to the world origin
        ty = (Dy - T2 * np.sin(alphr) - T1 * np.tan(alphr)) * np.cos(
            alphr
        ) - dy
        # z-distance of the pattern origin to the world origin
        tz = (
            T2
            + (Dy - T2 * np.sin(alphr) - T1 * np.tan(alphr)) * np.sin(alphr)
            + T1 / np.cos(alphr)
        )
        # resulting translation vector
        Tvec = np.array([tx, ty, -tz], dtype="float32")

        # rotation around the x-axis (pattern coordinate system)
        xrot = np.array([1, 0, 0]) * np.radians(-alpha)
        xMat = cv2.Rodrigues(xrot)[0]

        # (really dirty method to get) rotation angle of the calibration board
        zrot = int(filename[-6:-4])
        zrot = (zrot - 1) * 10
        zrot = np.radians(zrot)
        zrot = np.matmul(xMat, np.array([0, 0, 1])) * zrot
        zMat = cv2.Rodrigues(zrot)[0]

        # absolute world vectors equivalent to cv2 tvec and rvec:
        tvecW = np.matmul(cv2.Rodrigues(rvec)[0], Tvec) + tvec.T
        rvecW = cv2.Rodrigues(
            np.matmul(cv2.Rodrigues(rvec)[0], np.matmul(zMat, xMat))
        )[0]
        #        embed()

        projection_matrix[ind, 0:4, 0:4] = utils.rodrigues_to_matrix(rvecW)
        projection_matrix[ind, 0:3, 3] = tvecW
        projection_matrix[ind, 3, 3] = 1

        ind += 1

        if impose_cube:
            new_object_points = (
                np.array(
                    [
                        [0, 0, 0],
                        [0, 1, 0],
                        [1, 0, 0],
                        [1, 1, 0],
                        [0, 0, 1],
                        [0, 1, 1],
                        [1, 0, 1],
                        [1, 1, 1],
                    ],
                    dtype=np.float32,
                )
                * 0.04
            )

            world_origin_points = (
                np.array(
                    [
                        [0, 0, 0],
                        [0, 1, 0],
                        [1, 0, 0],
                        [0, 0, 1],
                    ],
                    dtype=np.float32,
                )
                * 0.1
            )

            world_origin_points = utils.rot_points(xMat, world_origin_points)
            world_origin_points = utils.rot_points(zMat, world_origin_points)
            world_origin_points = world_origin_points + Tvec

            # cube
            point_pairs = (
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
                (0, 1),
                (0, 2),
                (1, 3),
                (2, 3),
                (4, 5),
                (4, 6),
                (5, 7),
                (6, 7),
            )

            img = cv2.imread(filename)
            imgpoints, _ = cv2.projectPoints(
                new_object_points,
                rvec,
                tvec,
                camera_matrix,
                dist_coeffs,
            )

            for p1, p2 in point_pairs:
                cv2.line(
                    img,
                    tuple(imgpoints[p1, 0]),
                    tuple(imgpoints[p2, 0]),
                    [200, 200, 0],
                    thickness=2,
                )

            # world origin
            point_pairs = (
                (0, 1),
                (0, 2),
                (0, 3),
            )

            imgpoints, _ = cv2.projectPoints(
                world_origin_points,
                rvec,
                tvec,
                camera_matrix,
                dist_coeffs,
            )

            for p1, p2 in point_pairs:
                cv2.line(
                    img,
                    tuple(imgpoints[p1, 0]),
                    tuple(imgpoints[p2, 0]),
                    [200, 200, 0],
                    thickness=2,
                )

            cv2.imshow("Imposed Cube", img)
            cv2.waitKey(100)

    cv2.destroyAllWindows()

    projection_matrix_std = np.std(projection_matrix, axis=0)
    projection_matrix = np.mean(projection_matrix, axis=0)

    print("Mean proj matrix:")
    print(projection_matrix)
    print("Std proj matrix:")
    print(projection_matrix_std)
    print("Rel std proj matrix:")
    print(projection_matrix_std / projection_matrix)

    # save all the data
    calibration_data = dict()
    calibration_data["camera_matrix"] = dict()
    calibration_data["camera_matrix"]["rows"] = 3
    calibration_data["camera_matrix"]["cols"] = 3
    calibration_data["camera_matrix"][
        "data"
    ] = camera_matrix.flatten().tolist()
    calibration_data["distortion_coefficients"] = dict()
    calibration_data["distortion_coefficients"]["rows"] = 1
    calibration_data["distortion_coefficients"]["cols"] = 5
    calibration_data["distortion_coefficients"][
        "data"
    ] = dist_coeffs.flatten().tolist()

    calibration_data["projection_matrix"] = dict()
    calibration_data["projection_matrix"]["rows"] = 4
    calibration_data["projection_matrix"]["cols"] = 4
    calibration_data["projection_matrix"][
        "data"
    ] = projection_matrix.flatten().tolist()

    calibration_data["projection_matrix_std"] = dict()
    calibration_data["projection_matrix_std"]["rows"] = 4
    calibration_data["projection_matrix_std"]["cols"] = 4
    calibration_data["projection_matrix_std"][
        "data"
    ] = projection_matrix_std.flatten().tolist()

    with open(extrinsic_calibration_filename, "w") as outfile:
        yaml.dump(
            calibration_data,
            outfile,
            default_flow_style=False,
        )


def main():
    """Execute an action depending on arguments passed by the user."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "intrinsic_calibration",
            "extrinsic_calibration",
            "extrinsic_mean",
        ],
        help="""Action that is executed.""",
    )

    parser.add_argument(
        "--intrinsic_calibration_filename",
        type=str,
        help="""Filename used for saving intrinsic calibration
                        data or loading it""",
    )

    parser.add_argument(
        "--calibration_data",
        type=str,
        help="""Path to the calibration data directory .""",
    )

    parser.add_argument(
        "--extrinsic_calibration_filename",
        type=str,
        help="""Filename used for saving intrinsic calibration
                         data.""",
    )
    parser.add_argument(
        "--image_view_filename",
        type=str,
        help="""Image with charuco centralized at the (0, 0, 0)
                        position.""",
    )

    args = parser.parse_args()

    if args.action == "intrinsic_calibration":
        if not args.intrinsic_calibration_filename:
            raise RuntimeError("intrinsic_calibration_filename not specified.")
        if not args.calibration_data:
            raise RuntimeError("calibration_data not specified.")
        calibrate_intrinsic_parameters(
            args.calibration_data, args.intrinsic_calibration_filename
        )
    elif args.action == "extrinsic_calibration":
        if not args.intrinsic_calibration_filename:
            raise RuntimeError("intrinsic_calibration_filename not specified.")
        if not args.extrinsic_calibration_filename:
            raise RuntimeError("extrinsic_calibration_filename not specified.")
        if not args.image_view_filename:
            raise RuntimeError("image_view_filename not specified.")
        calibrate_extrinsic_parameters(
            args.intrinsic_calibration_filename,
            args.image_view_filename,
            args.extrinsic_calibration_filename,
            impose_cube=True,
        )

    elif args.action == "extrinsic_mean":

        if (
            not args.calibration_data
            and not args.intrinsic_calibration_filename
        ):
            raise RuntimeError(
                "neither calibration_data nor intrinsic_calibration_filename not specified."
            )

        if not args.extrinsic_calibration_filename:
            raise RuntimeError("extrinsic_calibration_filename not specified.")

        if args.intrinsic_calibration_filename:
            with open(args.intrinsic_calibration_filename) as file:
                calibration_data = yaml.safe_load(file)

            def config_matrix(data):
                return np.array(data["data"]).reshape(
                    data["rows"], data["cols"]
                )

            camera_matrix = config_matrix(calibration_data["camera_matrix"])
            dist_coeffs = config_matrix(
                calibration_data["distortion_coefficients"]
            )
        else:
            camera_matrix, dist_coeffs = calibrate_intrinsic_parameters(
                args.calibration_data, args.extrinsic_calibration_filename
            )

        calibrate_mean_extrinsic_parameters(
            camera_matrix,
            dist_coeffs,
            args.calibration_data,
            args.extrinsic_calibration_filename,
            impose_cube=True,
        )


if __name__ == "__main__":
    main()
