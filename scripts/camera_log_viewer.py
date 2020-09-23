#!/usr/bin/env python3
"""
Play back CameraObservations from a log file.
"""
import argparse
import cv2

import trifinger_cameras
from trifinger_cameras import utils


def main():
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "filename",
        type=str,
        help="""Path to the log file.""",
    )
    args = argparser.parse_args()

    log_reader = trifinger_cameras.camera.LogReader(args.filename)

    # determine rate based on time stamps
    start_time = log_reader.data[0].timestamp
    end_time = log_reader.data[-1].timestamp
    interval = (end_time - start_time) / len(log_reader.data)
    # convert to ms
    interval = int(interval * 1000)

    print(
        "Loaded {} frames at an average interval of {} ms ({:.1f} fps)".format(
            len(log_reader.data), interval, 1000 / interval
        )
    )

    for observation in log_reader.data:
        cv2.imshow("Image", utils.convert_image(observation.image))

        # stop if either "q" or ESC is pressed
        if cv2.waitKey(interval) in [ord("q"), 27]:  # 27 = ESC
            break


if __name__ == "__main__":
    main()
