#!/usr/bin/env python3
"""Try to connect to the cameras one by one to detect failures."""
import sys

import trifinger_cameras


def main():
    has_failure = False
    for name in ("camera60", "camera180", "camera300"):
        try:
            trifinger_cameras.camera.PylonDriver(name)
            print("{}: okay".format(name))
        except RuntimeError as e:
            print("{}: FAILED".format(name))
            has_failure = True

    if has_failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
