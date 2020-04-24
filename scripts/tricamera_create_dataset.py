#!/usr/bin/env python3
import argparse
import numpy as np
import cv2
import pickle
import os

import robot_interfaces


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument( "--outdir", "-o", type=str,
                           help="""Output directory.""")
    args = argparser.parse_args()

    camera_data = robot_interfaces.tricamera.Data()
    camera_names = ["camera60", "camera180", "camera300"]
    camera_driver = robot_interfaces.tricamera.TriCameraDriver(
        *camera_names
    )

    camera_backend = robot_interfaces.tricamera.Backend(
        camera_driver, camera_data
    )
    camera_frontend = robot_interfaces.tricamera.Frontend(camera_data)

    counter = 0
    while True:
        counter += 1
        sample_name = "{:04d}".format(counter)
        directory = os.path.join(args.outdir, sample_name)
        if os.path.exists(directory):
            print("skip existing sample {}".format(sample_name))
            continue

        input("Press Enter to record sample {}".format(sample_name))
        os.makedirs(directory)

        observation = camera_frontend.get_latest_observation()

        for i, name in enumerate(camera_names):
            filename = os.path.join(directory, name + ".png")
            cv2.imwrite(filename, np.array(observation.cameras[i].image,
                                           copy=False))


if __name__ == "__main__":
    main()
