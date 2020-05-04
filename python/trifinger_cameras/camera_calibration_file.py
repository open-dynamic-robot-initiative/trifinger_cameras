import yaml
import numpy as np


def config_to_array(data):
    """Convert a dictionary with keys "data", "rows" and "cols" to an array.

    Args:
        data (dict):  Dictionary containing the following keys:
            - "data": a flat list with the array data.
            - "rows": The number of rows in the array.
            - "cols": The number of columns in the array.

    Returns:
        The given data as an array of shape ("rows", "cols").
    """
    return np.array(data["data"]).reshape(data["rows"], data["cols"])


class CameraCalibrationFile:
    """Simplifies access to the data in a camera calibration file."""

    def __init__(self, filename):
        """Load the file.

        Args:
            filename (str):  Path to the calibration YAML file.
        """
        self.filename = filename

        with open(filename) as file:
            self.data = yaml.safe_load(file)

    def __getitem__(self, name):
        """Get the specified array from the calibration data.

        Args:
            name (str):  Name of the array.

        Returns:
            (numpy.array):  The array with the specified name.
        """
        return config_to_array(self.data[name])
