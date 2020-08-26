#!/usr/bin/env python3
"""Interactive Recording of camera images.

Accesses the camera(s) via the camera interface from robot_interfaces and
stores a frame every time the user presses enter.

By default the three-camera-setup of the TriFinger platform is used but it can
be changed to using a single camera either via Pylon or OpenCV with the
`--driver` argument.
"""
import argparse
import os

import cv2

import trifinger_cameras
from trifinger_cameras import utils


class SingleImageSaver:
    def __init__(self, out_dir, camera_name):
        self.counter = 0
        self.out_dir = out_dir
        self.sample_name_fmt = "{{:04d}}_{}.png".format(camera_name)

    def next(self):
        self.counter += 1
        self.sample_name = self.sample_name_fmt.format(self.counter)
        return self.sample_name

    def exists(self):
        filename = os.path.join(self.out_dir, self.sample_name)
        return os.path.exists(filename)

    def save(self, observation):
        filename = os.path.join(self.out_dir, self.sample_name)
        image = utils.convert_image(observation.image)
        cv2.imwrite(filename, image)


class TriImageSaver:
    def __init__(self, out_dir, camera_names):
        self.counter = 0
        self.out_dir = out_dir
        self.camera_names = camera_names
        self.sample_name_fmt = "{:04d}"

    def next(self):
        self.counter += 1
        self.sample_name = self.sample_name_fmt.format(self.counter)
        return self.sample_name

    def exists(self):
        directory = os.path.join(self.out_dir, self.sample_name)
        return os.path.exists(directory)

    def save(self, observation):
        directory = os.path.join(self.out_dir, self.sample_name)
        os.makedirs(directory)

        for i, name in enumerate(self.camera_names):
            filename = os.path.join(directory, name + ".png")
            image = utils.convert_image(observation.cameras[i].image)
            cv2.imwrite(filename, image)


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "--outdir", "-o", type=str, required=True, help="""Output directory."""
    )
    argparser.add_argument(
        "--trigger-interval",
        type=float,
        metavar="INTERVAL",
        help="""Automatically record frames in the specified interval (in
            seconds).  If this is set, a live stream of the camera is shown and
            recording is triggered automatically every INTERVAL seconds.
            If not set, the script waits for the user to press Enter to record
            frames (in this case, no live stream is shown).
        """,
    )
    argparser.add_argument(
        "--driver",
        default="tri",
        choices=("tri", "pylon", "opencv"),
        help="""Which camera driver to use.  Use "tri" for the three-camera
            setup (using Pylon), "pylon" for a single Pylon camera and "opencv"
            for an arbitrary camera that is supported by OpenCV.  Default is
            "%(default)s".
        """,
    )
    argparser.add_argument(
        "--camera-id",
        "-c",
        help="""ID of the camera that is used.  Depends on the setting of
            --driver:  If the "pylon" driver is used this refers to the
            DeviceUserId, in case of "opencv" it is the index of the device.
            For the "tri" driver, this value is ignored.
        """,
    )
    args = argparser.parse_args()

    if args.driver != "tri" and args.camera_id is None:
        print("You need to specify --camera-id")
        return

    if args.driver == "tri":
        camera_names = ["camera60", "camera180", "camera300"]
        camera_driver = trifinger_cameras.tricamera.TriCameraDriver(
            *camera_names
        )
        camera_module = trifinger_cameras.tricamera
        image_saver = TriImageSaver(args.outdir, camera_names)
    elif args.driver == "pylon":
        camera_driver = trifinger_cameras.camera.PylonDriver(args.camera_id)
        camera_module = trifinger_cameras.camera
        image_saver = SingleImageSaver(args.outdir, args.camera_id)
    elif args.driver == "opencv":
        camera_driver = trifinger_cameras.camera.OpenCVDriver(
            int(args.camera_id)
        )
        camera_module = trifinger_cameras.camera
        image_saver = SingleImageSaver(args.outdir, args.camera_id)

    camera_data = camera_module.SingleProcessData()
    camera_backend = camera_module.Backend(camera_driver, camera_data)  # noqa
    camera_frontend = camera_module.Frontend(camera_data)

    while True:
        sample_name = image_saver.next()
        if image_saver.exists():
            print("skip existing sample {}".format(sample_name))
            continue

        if args.trigger_interval:
            interval_ms = 10
            steps = int(args.trigger_interval * 1000 / interval_ms)
            for i in range(steps):
                observation = camera_frontend.get_latest_observation()
                if args.driver == "tri":
                    for i, name in enumerate(camera_names):
                        image = utils.convert_image(observation.cameras[i].image)
                        cv2.imshow(name, image)
                else:
                    image = utils.convert_image(observation.image)
                    cv2.imshow(args.camera_id, image)
                cv2.waitKey(interval_ms)
            print("Record sample {}".format(sample_name))

        else:
            input("Press Enter to record sample {}".format(sample_name))

        observation = camera_frontend.get_latest_observation()
        image_saver.save(observation)


if __name__ == "__main__":
    main()
