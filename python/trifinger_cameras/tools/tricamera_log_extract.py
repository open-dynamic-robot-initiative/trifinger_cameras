"""Extract images from a TriCamera log file."""

import argparse
import pathlib
import sys
import cv2

from trifinger_cameras import utils


def tricamera_log_extract(log_reader_class) -> None:  # noqa: ANN001
    """Extract images from a TriCamera log file.

    Args:
        LogReader: LogReader class that can read the log file.  For log files recorded
        with this package, use :class:`trifinger_cameras.tricamera.LogReader`.  By
        passing the equivalent class of ``trifinger_object_tracking`` the same function
        can be used to load log files that include object data.
    """
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "filename",
        type=str,
        help="""Path to the log file.""",
    )
    argparser.add_argument(
        "output_dir",
        type=str,
        help="Directory to which images are stored.",
    )
    argparser.add_argument(
        "--step",
        "-s",
        type=int,
        metavar="n",
        help="Extract only every n-th frame.",
    )
    args = argparser.parse_args()

    out_dir = pathlib.Path(args.output_dir)

    if not out_dir.is_dir():
        print("{} does not exist or is not a directory".format(out_dir))
        sys.exit(1)

    log_reader = log_reader_class(args.filename)

    for i, observation in enumerate(log_reader.data[:: args.step]):
        observation_dir = out_dir / ("%04d" % (i + 1))
        observation_dir.mkdir()
        for camera_idx, name in enumerate(["camera60", "camera180", "camera300"]):
            image = utils.convert_image(observation.cameras[camera_idx].image)
            img_path = observation_dir / "{}.png".format(name)
            cv2.imwrite(str(img_path), image)
