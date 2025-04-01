#!/usr/bin/env python3
"""Calibrate cameras of the TriFingerPro platform.

Calibrates the cameras based on a set of images recorded with the TriFingerPro
calibration board holder.
"""

from __future__ import annotations

import argparse
import os

import cv2
import numpy as np
import yaml
from ruamel.yaml import YAML

from trifinger_cameras import utils
from trifinger_cameras.charuco_board_handler import CharucoBoardHandler


BOARD_SIZE_X = 5
BOARD_SIZE_Y = 10
BOARD_SQUARE_SIZE = 0.04
BOARD_MARKER_SIZE = 0.03


class CameraParameters:
    camera_name: str
    image_width: int
    image_height: int
    camera_matrix: np.ndarray
    dist_coeffs: np.ndarray
    tf_world_to_camera: np.ndarray
    tf_world_to_camera_std: np.ndarray


def get_image_files(data_dir: str, camera_name: str) -> list[str]:
    image_paths: list[str] = []

    # We expect image directories 0001 to 0036
    filename = camera_name + ".png"
    for i in range(1, 37):
        subdir_name = "{:04d}".format(i)
        image_path = os.path.join(data_dir, subdir_name, filename)

        if not os.path.exists(image_path):
            raise RuntimeError("{} does not exist".format(image_path))

        image_paths.append(image_path)

    return image_paths


def calibrate_intrinsic_parameters(
    image_files: list[str], visualize: bool = False
) -> tuple[np.ndarray, np.ndarray]:
    """Calibrate intrinsic parameters of the camera given different images
    taken for the Charuco board from different views, the resulting parameters
    are saved to the provided filename.

    Args:
        image_files:  List of calibration image files.
        visualize:  If true, show visualization of the board detection.
    """
    handler = CharucoBoardHandler(
        BOARD_SIZE_X, BOARD_SIZE_Y, BOARD_SQUARE_SIZE, BOARD_MARKER_SIZE
    )

    camera_matrix, dist_coeffs, error = handler.calibrate(
        image_files, visualize=visualize
    )

    return camera_matrix, dist_coeffs


def calibrate_mean_extrinsic_parameters(
    camera_matrix: np.ndarray,
    dist_coeffs: np.ndarray,
    image_files: list[str],
    impose_cube: bool = True,
) -> CameraParameters:
    """Calibrate extrinsic parameters of the camera.

    Calibrate extrinsic parameters given several images taken of the Charuco
    board at defined poses.  Transform the extrinsic parameters into the fixed
    'world' coordinate system.  The resulting parameters are averaged for all
    images and saved to the provided filename.

    Args:
        camera_matrix, dist_coeffs:  output of the intrinsic calibration
            (either read from file or directly obtained from intrinsic calibration
            function).
        image_files: list of image files.  taken for the Charuco board centered at
            (0, 0, 0).  to write the extrinsic calibration results in.
        impose_cube: boolean whether to output a virtual cube imposed on the first
            square of the board or not.

    Returns:
        The camera parameters including the camera pose.
    """

    handler = CharucoBoardHandler(
        BOARD_SIZE_X,
        BOARD_SIZE_Y,
        BOARD_SQUARE_SIZE,
        BOARD_MARKER_SIZE,
        camera_matrix,
        dist_coeffs,
    )

    camera_params = CameraParameters()

    pose_matrix = np.zeros((len(image_files), 4, 4))

    for i, filename in enumerate(image_files):
        # verify that images are given in the expected order
        assert "{:04d}".format(i + 1) in filename

        img = cv2.imread(filename)

        camera_params.image_height = img.shape[0]
        camera_params.image_width = img.shape[1]

        rvec, tvec = handler.detect_board_in_image(filename, visualize=False)

        # geometric data of the calibration board with respect to the 'world'
        # coordinates

        # inclination angle of the board (CAD data)
        alpha = 22
        alphr = np.radians(alpha)
        # half-width of the calibration board (CAD data)
        Dx = 0.105
        # projected (on the base) half-height of the calibration board (CAD
        # data)
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
        ty = (Dy - T2 * np.sin(alphr) - T1 * np.tan(alphr)) * np.cos(alphr) - dy
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

        # get rotation angle of the calibration board
        zrot = i + 1
        zrot = (zrot - 1) * 10
        zrot = np.radians(zrot)
        zrot = np.matmul(xMat, np.array([0, 0, 1])) * zrot
        zMat = cv2.Rodrigues(zrot)[0]

        # absolute world vectors equivalent to cv2 tvec and rvec:
        tvecW = np.matmul(cv2.Rodrigues(rvec)[0], Tvec) + tvec.T
        rvecW = cv2.Rodrigues(np.matmul(cv2.Rodrigues(rvec)[0], np.matmul(zMat, xMat)))[
            0
        ]

        pose_matrix[i, 0:4, 0:4] = utils.rodrigues_to_matrix(rvecW)
        pose_matrix[i, 0:3, 3] = tvecW
        pose_matrix[i, 3, 3] = 1

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

            world_origin_points = (zMat @ xMat @ world_origin_points.T).T
            world_origin_points = world_origin_points + Tvec

            # cube
            cube_point_pairs = (
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

            for p1, p2 in cube_point_pairs:
                cv2.line(
                    img,
                    tuple(imgpoints[p1, 0].astype(int)),
                    tuple(imgpoints[p2, 0].astype(int)),
                    [200, 200, 0],
                    thickness=2,
                )

            # world origin
            origin_frame_point_pairs = (
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

            for p1, p2 in origin_frame_point_pairs:
                cv2.line(
                    img,
                    tuple(imgpoints[p1, 0].astype(int)),
                    tuple(imgpoints[p2, 0].astype(int)),
                    [200, 200, 0],
                    thickness=2,
                )

            cv2.imshow("Imposed Cube", img)
            cv2.waitKey(100)

    cv2.destroyAllWindows()

    camera_params.camera_matrix = camera_matrix
    camera_params.dist_coeffs = dist_coeffs
    camera_params.tf_world_to_camera_std = np.std(pose_matrix, axis=0)
    camera_params.tf_world_to_camera = np.mean(pose_matrix, axis=0)

    print("Mean proj matrix:")
    print(camera_params.tf_world_to_camera)
    print("Std proj matrix:")
    print(camera_params.tf_world_to_camera_std)
    print("Rel std proj matrix:")
    print(camera_params.tf_world_to_camera_std / camera_params.tf_world_to_camera)

    return camera_params


def save_parameter_file(params: CameraParameters, filename: str) -> None:
    # save all the data
    calibration_data = {
        "camera_name": params.camera_name,
        "image_height": params.image_height,
        "image_width": params.image_width,
    }

    calibration_data["camera_matrix"] = {
        "rows": 3,
        "cols": 3,
        "dt": "d",
        "data": params.camera_matrix.flatten().tolist(),
    }

    calibration_data["distortion_coefficients"] = {
        "rows": 1,
        "cols": 5,
        "dt": "d",
        "data": params.dist_coeffs.flatten().tolist(),
    }

    calibration_data["tf_world_to_camera"] = {
        "rows": 4,
        "cols": 4,
        "dt": "d",
        "data": params.tf_world_to_camera.flatten().tolist(),
    }

    calibration_data["tf_world_to_camera_std"] = {
        "rows": 4,
        "cols": 4,
        "dt": "d",
        "data": params.tf_world_to_camera_std.flatten().tolist(),
    }

    ryaml = YAML()
    ryaml.version = (1, 1)  # type: ignore[assignment]
    ryaml.explicit_start = True  # type: ignore[assignment]
    # indent lists in opencv-compatible way
    ryaml.indent(offset=2)

    with open(filename, "w") as outfile:
        ryaml.dump(
            calibration_data,
            outfile,
        )


def main() -> None:
    """Execute an action depending on arguments passed by the user."""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--calibration-data",
        "-d",
        type=str,
        help="""Path to the calibration data directory .""",
    )

    parser.add_argument(
        "--camera-name",
        "-c",
        choices=["camera60", "camera180", "camera300"],
        required=True,
        help="""Name of the camera.""",
    )

    parser.add_argument(
        "--output-file-prefix",
        type=str,
        help="Prefix for the output files. If not set the camera name is used",
    )

    parser.add_argument(
        "--visualize",
        "-v",
        action="store_true",
        help="Visualize board detection.",
    )

    parser.add_argument(
        "--intrinsic-file",
        type=str,
        help="""Load intrinsic parameters from this file.
            If not specified, they are computed from the images.
        """,
    )

    args = parser.parse_args()

    if args.output_file_prefix:
        output_file_prefix = args.output_file_prefix
    else:
        output_file_prefix = args.camera_name

    output_file_full = output_file_prefix + "_full.yml"
    output_file_cropped = output_file_prefix + "_cropped.yml"
    output_file_cropped_and_downsampled = (
        output_file_prefix + "_cropped_and_downsampled.yml"
    )

    image_files = get_image_files(args.calibration_data, args.camera_name)

    if args.intrinsic_file:
        with open(args.intrinsic_file) as file:
            calibration_data = yaml.safe_load(file)

        def config_matrix(data: dict) -> np.ndarray:
            return np.array(data["data"]).reshape(data["rows"], data["cols"])

        camera_matrix = config_matrix(calibration_data["camera_matrix"])
        dist_coeffs = config_matrix(calibration_data["distortion_coefficients"])
    else:
        camera_matrix, dist_coeffs = calibrate_intrinsic_parameters(
            image_files, args.visualize
        )

    camera_params = calibrate_mean_extrinsic_parameters(
        camera_matrix,
        dist_coeffs,
        image_files,
        impose_cube=args.visualize,
    )

    camera_params.camera_name = args.camera_name

    save_parameter_file(camera_params, output_file_full)

    # adjust for cropped images (shift the image center)
    camera_params.image_height = 540
    camera_params.image_width = 540
    camera_params.camera_matrix[0, 2] -= 88
    save_parameter_file(camera_params, output_file_cropped)

    # adjust for downsampled images (divide pixel values by 2)
    camera_params.image_height = camera_params.image_height // 2
    camera_params.image_width = camera_params.image_width // 2
    camera_params.camera_matrix[:2, :] /= 2
    save_parameter_file(camera_params, output_file_cropped_and_downsampled)


if __name__ == "__main__":
    main()
