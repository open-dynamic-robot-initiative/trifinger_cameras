#!/usr/bin/env python3
"""Convert TriCameraObservation log file to hdf5."""

import argparse
import pathlib
import sys

import h5py
import numpy as np

from trifinger_cameras import CAMERA_NAMES, TRICAMERA_LOG_MAGIC, tricamera
from trifinger_cameras.camera_calibration_file import CameraCalibrationFile


def main() -> int:
    """Main entry point of the script."""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--logfile",
        "-l",
        type=pathlib.Path,
        required=True,
        help="Path to the log file.",
    )
    argparser.add_argument(
        "--outfile",
        "-o",
        type=pathlib.Path,
        required=True,
        help="Path to the output hdf5 file.",
    )
    # Add arguments for calibration files
    argparser.add_argument(
        "--camera-info",
        "-c",
        type=pathlib.Path,
        nargs=3,
        required=True,
        help="Paths to the three camera calibration YAML files.",
    )
    args = argparser.parse_args()

    if not args.logfile.is_file():
        print("Log file does not exist.", file=sys.stderr)
        return 1

    if args.outfile.exists():
        print("Output file already exists.  Exiting.", file=sys.stderr)
        return 1

    # Load calibration files
    camera_params = []
    for calib_file in args.camera_info:
        if not calib_file.is_file():
            print(f"Calibration file {calib_file} does not exist.", file=sys.stderr)
            return 1
        camera_params.append(CameraCalibrationFile(calib_file))

    # Verify camera names match expected order
    for param, expected_name in zip(camera_params, CAMERA_NAMES):
        if param["camera_name"] != expected_name:
            print(
                f"Expected camera {expected_name} but got {param['camera_name']}",
                file=sys.stderr,
            )
            return 1

    log_reader = tricamera.LogReader(str(args.logfile))

    n_frames = len(log_reader.data)
    assert n_frames > 0, "No frames found in log file."

    img_shape = log_reader.data[0].cameras[0].image.shape

    # sanity check that the image size matches with camera info files
    for i, params in enumerate(camera_params):
        if (
            params["image_width"] != img_shape[1]
            or params["image_height"] != img_shape[0]
        ):
            print(
                f"Image size mismatch for camera {CAMERA_NAMES[i]}:"
                f" expected {img_shape[1]}x{img_shape[0]} (based on camera info) but"
                f" got {params['image_width']}x{params['image_height']}",
                file=sys.stderr,
            )
            return 1

    with h5py.File(args.outfile, "w") as h5:
        # create datasets for images and timestamps
        h5.create_dataset("camera_names", data=[name.encode() for name in CAMERA_NAMES])
        h5.attrs["magic"] = TRICAMERA_LOG_MAGIC
        h5.attrs["format_version"] = 2
        h5.attrs["num_cameras"] = len(CAMERA_NAMES)
        h5.attrs["image_width"] = img_shape[1]
        h5.attrs["image_height"] = img_shape[0]

        # Add camera calibration parameters
        calib_group = h5.create_group("camera_info")
        for i, params in enumerate(camera_params):
            cam_group = calib_group.create_group(CAMERA_NAMES[i])
            cam_group.create_dataset(
                "camera_matrix", data=params.get_array("camera_matrix")
            )
            cam_group.create_dataset(
                "distortion_coefficients",
                data=params.get_array("distortion_coefficients"),
            )
            cam_group.create_dataset(
                "tf_world_to_camera", data=params.get_array("tf_world_to_camera")
            )

        h5.create_dataset(
            "images",
            shape=(n_frames, len(CAMERA_NAMES), img_shape[0], img_shape[1]),
            dtype=np.uint8,
            chunks=(1, len(CAMERA_NAMES), img_shape[0], img_shape[1]),
            compression="gzip",
            shuffle=True,
        )

        h5.create_dataset(
            "timestamps",
            shape=(n_frames, len(CAMERA_NAMES)),
            dtype=np.double,
        )

        for i_obs, observation in enumerate(log_reader.data):
            cameras = observation.cameras
            h5["images"][i_obs] = [camera.image for camera in cameras]
            h5["timestamps"][i_obs] = [camera.timestamp for camera in cameras]

    return 0


if __name__ == "__main__":
    sys.exit(main())
