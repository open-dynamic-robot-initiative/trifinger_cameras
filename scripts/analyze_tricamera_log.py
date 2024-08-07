#!/usr/bin/env python3
"""
Analyze a TriCameraObservation log file.
"""
import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt

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

    log_reader = trifinger_cameras.tricamera.LogReader(args.filename)

    # determine rate based on time stamps
    start_time = log_reader.data[0].cameras[0].timestamp
    end_time = log_reader.data[-1].cameras[0].timestamp
    duration = end_time - start_time
    interval = duration / len(log_reader.data)
    # convert to ms
    interval = int(interval * 1000)

    print(
        "Loaded {} frames at an average interval of {} ms ({:.1f} fps)".format(
            len(log_reader.data), interval, 1000 / interval
        )
    )
    print("Total duration: {:.1f} seconds".format(duration))

    stamps = [
        np.array([observation.cameras[c].timestamp for observation in log_reader.data])
        for c in range(3)
    ]

    fig, axes = plt.subplots(2, 3)

    for i in range(3):
        axes[0, i].plot(stamps[i])
        axes[0, i].set_title("camera {}".format(i))

    for i, (a, b) in enumerate(((0, 1), (0, 2), (1, 2))):
        # convert diffs to miliseconds
        diffs = (stamps[a] - stamps[b]) * 1000
        axes[1, i].plot(diffs)
        axes[1, i].set_title("diff {} - {}".format(a, b))
        axes[1, i].set_ylabel("Milliseconds")

        diffs = np.abs(diffs)
        print("Time differences {} - {}".format(a, b))
        print("\tmean: {:.4f} ms".format(diffs.mean()))
        print("\tmin: {:.4f} ms".format(diffs.min()))
        print("\tmax: {:.4f} ms".format(diffs.max()))

    plt.show()


if __name__ == "__main__":
    main()
