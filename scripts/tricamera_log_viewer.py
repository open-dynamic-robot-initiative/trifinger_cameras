#!/usr/bin/env python3
"""Play back TriCameraObservations from a log file."""

from __future__ import annotations

import argparse
import pathlib
import time
from typing import Generator

import cv2
import numpy as np

import trifinger_cameras
from trifinger_cameras import utils


def read_sensor_log(filename: pathlib.Path) -> Generator[tuple[int, np.ndarray]]:
    t_start = time.monotonic()
    log_reader = trifinger_cameras.tricamera.LogReader(str(filename))
    t_end = time.monotonic()
    print("Time for reading log file: {:.3f} s".format(t_end - t_start))

    # determine rate based on time stamps
    start_time = log_reader.data[0].cameras[0].timestamp
    end_time = log_reader.data[-1].cameras[0].timestamp
    interval = (end_time - start_time) / len(log_reader.data)
    # convert to ms
    interval = int(interval * 1000)

    print(
        "Loaded {} frames at an average interval of {} ms ({:.1f} fps)".format(
            len(log_reader.data), interval, 1000 / interval
        )
    )

    for observation in log_reader.data:
        img = np.hstack(
            [
                utils.convert_image(observation.cameras[0].image),
                utils.convert_image(observation.cameras[1].image),
                utils.convert_image(observation.cameras[2].image),
            ]
        )
        yield interval, img


def read_hdf5(filename: pathlib.Path) -> Generator[tuple[int, np.ndarray]]:
    import h5py

    with h5py.File(filename, "r") as h5:
        if h5.attrs.get("magic") != trifinger_cameras.TRICAMERA_LOG_MAGIC:
            msg = "Input file doesn't seem to be a TriCamera log file (bad magic byte)."
            raise ValueError(msg)
        if h5.attrs["format_version"] not in (1, 2):
            msg = f"Unsupported file format version {h5.attrs['format_version']}"
            raise ValueError(msg)

        timestamps = h5["timestamps"]
        # determine rate based on first and last time stamp
        interval = int((timestamps[-1][0] - timestamps[0][0]) / len(timestamps) * 1000)
        print(
            "Loaded {} frames at an average interval of {} ms ({:.1f} fps)".format(
                len(h5["images"]), interval, 1000 / interval
            )
        )

        for images in h5["images"]:
            img = np.hstack([utils.convert_image(img) for img in images])
            yield interval, img


def indicate_clipping(image: np.ndarray) -> np.ndarray:
    """Set clipped pixels to pure red."""
    # image = image.copy()

    # set clipped pixels to pure red
    image[image[:, :, 0] == 255] = [0, 0, 255]
    image[image[:, :, 1] == 255] = [0, 0, 255]
    image[image[:, :, 2] == 255] = [0, 0, 255]
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filename",
        type=pathlib.Path,
        help="""Path to the log file.""",
    )
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed.")
    parser.add_argument(
        "--skip", type=int, default=0, metavar="n", help="Skip the first n frames."
    )
    parser.add_argument(
        "--indicate-clipping",
        action="store_true",
        help="Visualize clipped pixels by setting them to pure red.",
    )
    args = parser.parse_args()

    window_title = " | ".join(trifinger_cameras.CAMERA_NAMES)
    read_func = (
        read_hdf5 if args.filename.suffix in (".h5", ".hdf5") else read_sensor_log
    )

    try:
        frame_number = 0
        for interval, image in read_func(args.filename):
            frame_number += 1
            if frame_number <= args.skip:
                continue

            if args.indicate_clipping:
                image = indicate_clipping(image)

            cv2.putText(
                image,
                f"Frame {frame_number}",
                (10, image.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
            )

            cv2.imshow(window_title, image)

            scaled_interval = int(interval / args.speed)
            # stop if either "q" or ESC is pressed
            if cv2.waitKey(max(scaled_interval, 1)) in [ord("q"), 27]:  # 27 = ESC
                break
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
