#!/usr/bin/env python3
"""Show live image of a Pylon camera and indicate whether it passes the sharpness test.

The sharpness of the image is evaluated by running Canny edge detection on the image and
computing the mean value of the resulting edge image.  A higher value means more edges
which indicates a sharper image.

The parameters can be adjusted via sliders in the GUI (note that the sliders in the GUI
only support integer values).

This test is also performed in robot_fingers/trifingerpro_post_submission.py.
"""

from __future__ import annotations
import argparse
import dataclasses
import typing
from collections import deque

import cv2
import numpy as np

import trifinger_cameras
from trifinger_cameras import utils


def add_label(
    image: np.ndarray, label: str, position: typing.Literal["top", "bottom"]
) -> np.ndarray:
    """Add label to the given image.

    Args:
        image: The image.
        label: Text to be added.
        position: Where to add the label (either "top" or "bottom").

    Returns:
        Image with added label.
    """
    label_height = 20

    if position == "top":
        offset = 0
    elif position == "bottom":
        offset = image.shape[0] - label_height
    else:
        ValueError(f"Invalid position '{position}'")

    # darken label background
    row_slice = slice(offset, (offset + label_height))
    image[row_slice, :, :] = 0.3 * image[row_slice, :, :]

    image = cv2.putText(
        image,
        label,
        (5, offset + label_height - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
    )
    return image


def auto_canny_params(image: np.ndarray, sigma: float = 0.33) -> tuple[float, float]:
    median = np.median(image)
    lower = max(0, (1.0 - sigma) * median)
    upper = min(255, (1.0 + sigma) * median)

    return lower, upper


@dataclasses.dataclass
class Params:
    canny_threshold1: float
    canny_threshold2: float
    edge_mean_threshold: float

    def set_canny_threshold1(self, value: float) -> None:
        self.canny_threshold1 = value

    def set_canny_threshold2(self, value: float) -> None:
        self.canny_threshold2 = value

    def set_edge_mean_threshold(self, value: float) -> None:
        self.edge_mean_threshold = value


def main() -> None:
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "camera_id",
        type=str,
        help="""DeviceUserId of the camera that is used.""",
    )
    argparser.add_argument(
        "--canny",
        "-c",
        type=float,
        nargs=2,
        default=(25.0, 250.0),
        metavar=("THRESH1", "THRESH2"),
        help="Threshold parameters for the Canny algorithm.  Default: %(default)s.",
    )
    argparser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=10.0,
        help="""Threshold for the edge mean.  Images with an 'edge mean' below this
            threshold are marked as too blurry.  Default: %(default)s.
        """,
    )
    argparser.add_argument(
        "--buffer-size",
        type=int,
        default=3,
        help="Buffer size in seconds for the smoothed edge mean.",
    )
    argparser.add_argument(
        "--update-freq",
        type=float,
        default=10.0,
        help="""Frequency at which new images are fetched from the camera.  Should not
            be higher than the actual frame rate of the camera.
        """,
    )
    args = argparser.parse_args()

    camera_data = trifinger_cameras.camera.SingleProcessData()
    camera_driver = trifinger_cameras.camera.PylonDriver(args.camera_id)

    camera_backend = trifinger_cameras.camera.Backend(  # noqa: F841
        camera_driver, camera_data
    )
    camera_frontend = trifinger_cameras.camera.Frontend(camera_data)

    params = Params(args.canny[0], args.canny[1], args.threshold)

    mean_buffer: deque[float] = deque(
        [], maxlen=int(args.update_freq * args.buffer_size)
    )

    window_name = f"Image Stream [{args.camera_id}]"
    cv2.namedWindow(window_name)

    cv2.createTrackbar(
        "Canny threshold 1",
        window_name,
        0,
        max(200, params.canny_threshold1),
        params.set_canny_threshold1,
    )
    cv2.setTrackbarPos("Canny threshold 1", window_name, int(params.canny_threshold1))
    cv2.createTrackbar(
        "Canny threshold 2",
        window_name,
        0,
        max(400, params.canny_threshold2),
        params.set_canny_threshold2,
    )
    cv2.setTrackbarPos("Canny threshold 2", window_name, int(params.canny_threshold2))
    cv2.createTrackbar(
        "Edge mean threshold",
        window_name,
        0,
        max(30, params.edge_mean_threshold),
        params.set_edge_mean_threshold,
    )
    cv2.setTrackbarPos(
        "Edge mean threshold", window_name, int(params.edge_mean_threshold)
    )

    rate_ms = int(1000 / args.update_freq)
    while True:
        observation = camera_frontend.get_latest_observation()
        image = utils.convert_image(observation.image)

        edges_mean, edges = utils.check_image_sharpness(
            image, params.canny_threshold1, params.canny_threshold2
        )
        mean_buffer.append(edges_mean)
        mean_buffer_mean = np.mean(mean_buffer)

        image = np.hstack([image, np.dstack([~edges] * 3)])

        # add red or green border depending on whether edges_mean is above or below
        # threshold
        if mean_buffer_mean < params.edge_mean_threshold:
            border_color = (0, 0, 200)
        else:
            border_color = (0, 200, 0)
        border_width = 10
        image = cv2.copyMakeBorder(
            image,
            border_width,
            border_width,
            border_width,
            border_width,
            cv2.BORDER_CONSTANT,
            value=border_color,
        )

        add_label(image, args.camera_id, "top")
        add_label(
            image,
            "Canny mean: %.1f | smoothed: %.1f" % (edges_mean, mean_buffer_mean),
            "bottom",
        )

        cv2.imshow(window_name, image)

        # stop if either "q" or ESC is pressed
        if cv2.waitKey(rate_ms) in [ord("q"), 27]:  # 27 = ESC
            break


if __name__ == "__main__":
    main()
