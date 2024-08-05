#!/usr/bin/env python3
"""Overlay images from real cameras with rendered ones

With a slider, the transparency of the overlay layer can be changed to so one can switch
between either real or simulated images or blend them together.  This can be used to
validate how good the camera calibration is by checking how well the rendered images
match with the real ones.
"""
import argparse
import pathlib

import numpy as np
import cv2  # type: ignore

from trifinger_simulation import sim_finger, camera


SLIDER_MAX = 100
g_slider_value = 0


class BlendImages:
    def __init__(self, title, img1, img2):
        self.title = title
        self.img1 = img1
        self.img2 = img2

    def on_trackbar(self, val):
        alpha = val / SLIDER_MAX
        beta = 1.0 - alpha
        dst = cv2.addWeighted(self.img1, alpha, self.img2, beta, 0.0)
        cv2.imshow(self.title, dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config-dir",
        "-c",
        type=pathlib.Path,
        nargs="+",
        help="""Path to the directory containing camera calibration files. This
            is optional, if not specified, some default values will be used.
        """,
    )
    parser.add_argument(
        "--image-dir",
        "-i",
        type=pathlib.Path,
        help="""Path to the directory containing the real images.  If not set
            "{config_dir[0]}/0001" is used.
        """,
    )
    parser.add_argument(
        "--param-file-format",
        type=str,
        default="camera{id}_full.yml",
        help="""Format of the camera parameter files. '{id}' is replaced with
            the camera id.  Default: %(default)s
        """,
    )
    args = parser.parse_args()

    finger = sim_finger.SimFinger(
        finger_type="trifingerpro",
        enable_visualization=False,
    )
    finger.reset_finger_positions_and_velocities([-1.57, 1.57, -2.7] * 3)

    # load real images
    image_dir = args.image_dir if args.image_dir else args.config_dir[0] / "0001"
    print("image_dir:", image_dir)
    real_images = [
        cv2.imread(str(image_dir / "camera60.png")),
        cv2.imread(str(image_dir / "camera180.png")),
        cv2.imread(str(image_dir / "camera300.png")),
    ]
    real_images = np.hstack(real_images)

    blends = []

    def on_trackbar(val):
        for b in blends:
            b.on_trackbar(val)

    for config_dir in args.config_dir:
        cameras = camera.create_trifinger_camera_array_from_config(
            config_dir, calib_filename_pattern=args.param_file_format
        )

        # render images
        sim_images = cameras.get_images()
        # images are rgb --> convert to bgr for opencv
        sim_images = [
            cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in sim_images
        ]
        sim_images = np.hstack(sim_images)

        title_window = str(config_dir)

        blend = BlendImages(title_window, sim_images, real_images)
        blends.append(blend)

        cv2.namedWindow(title_window)
        trackbar_name = "Alpha x %d" % SLIDER_MAX
        cv2.createTrackbar(trackbar_name, title_window, 0, SLIDER_MAX, on_trackbar)
        # Show some stuff
        blend.on_trackbar(0)

    cv2.waitKey()


if __name__ == "__main__":
    main()
