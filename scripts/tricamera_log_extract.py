#!/usr/bin/env python3
"""Extract images from a TriCameraObservations log file."""

import trifinger_cameras
from trifinger_cameras.tools.tricamera_log_extract import tricamera_log_extract

if __name__ == "__main__":
    tricamera_log_extract(trifinger_cameras.tricamera.LogReader)
