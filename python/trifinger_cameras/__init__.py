# use "noqa" comments to silence flake8 warnings
# F401 = unused import, F403 = complaint about `import *`.
from . import py_camera_types as camera  # noqa: F401
from . import py_tricamera_types as tricamera  # noqa: F401


#: Names of the TriFinger cameras in the order in which they are usually handled.
CAMERA_NAMES = ("camera60", "camera180", "camera300")

#: Magic byte used to identify TriCamera logs (currently only used in HDF5 files).
TRICAMERA_LOG_MAGIC = 0x3CDA7A00
