#!/usr/bin/env python3
"""Convert TriCameraObservation log file to hdf5."""

import argparse
import pathlib
import sys

import cv2
import h5py
import numpy as np

import trifinger_cameras
from trifinger_cameras import utils

CAMERA_NAMES = ("camera60", "camera180", "camera300")


def main() -> int:
    """Main entry point of the script."""
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "logfile",
        type=pathlib.Path,
        help="Path to the log file.",
    )
    argparser.add_argument(
        "outfile",
        type=pathlib.Path,
        help="Path to the output hdf5 file.",
    )
    args = argparser.parse_args()

    if not args.logfile.is_file():
        print("Log file does not exist.", file=sys.stderr)
        return 1

    if args.outfile.exists():
        print("Output file already exists.  Exiting.", file=sys.stderr)
        return 1

    log_reader = trifinger_cameras.tricamera.LogReader(str(args.logfile))

    n_frames = len(log_reader.data)
    assert n_frames > 0, "No frames found in log file."

    img_shape = log_reader.data[0].cameras[0].image.shape

    with h5py.File(args.outfile, "w") as h5:
        # create datasets for images and timestamps
        h5.create_dataset("camera_names", data=[name.encode() for name in CAMERA_NAMES])
        h5.attrs["magic"] = 0x3CDA7A00
        h5.attrs["format_version"] = 1
        h5.attrs["num_cameras"] = len(CAMERA_NAMES)
        h5.attrs["image_width"] = img_shape[1]
        h5.attrs["image_height"] = img_shape[0]

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
