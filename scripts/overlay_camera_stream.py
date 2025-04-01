#!/usr/bin/env python3
"""Overlay an image on top of the camera stream."""
import argparse
import cv2

import trifinger_cameras
from trifinger_cameras import utils


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--camera-id",
        "-c",
        required=True,
        help="Camera name",
    )
    argparser.add_argument("--alpha", "-a", type=float, default=0.4)
    argparser.add_argument(
        "overlay_image",
        type=str,
    )
    args = argparser.parse_args()

    alpha = args.alpha
    overlay_image = cv2.imread(args.overlay_image)
    # use red channel only, so it is easy to distinguish from the actual image
    overlay_image[:, :, 0] = 0
    overlay_image[:, :, 1] = 0

    camera_data = trifinger_cameras.camera.SingleProcessData()
    camera_driver = trifinger_cameras.camera.PylonDriver(
        args.camera_id, downsample_images=False
    )
    camera_backend = trifinger_cameras.camera.Backend(  # noqa
        camera_driver, camera_data
    )
    camera_frontend = trifinger_cameras.camera.Frontend(camera_data)

    while True:
        observation = camera_frontend.get_latest_observation()
        image = utils.convert_image(observation.image)

        image = cv2.addWeighted(image, 1 - alpha, overlay_image, alpha, 0)

        cv2.imshow("Camera", image)
        # stop if either "q" or ESC is pressed
        if cv2.waitKey(10) in [ord("q"), 27]:  # 27 = ESC
            break


if __name__ == "__main__":
    main()
