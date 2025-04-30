from typing import Any

import yaml
import numpy as np


def config_to_array(data: dict) -> np.ndarray:
    """Convert a dictionary with keys "data", "rows" and "cols" to an array.

    Args:
        data:  Dictionary containing the following keys:
            - "data": a flat list with the array data.
            - "rows": The number of rows in the array.
            - "cols": The number of columns in the array.

    Returns:
        The given data as an array of shape ("rows", "cols").
    """
    return np.array(data["data"]).reshape(data["rows"], data["cols"])


class CameraCalibrationFile:
    """Simplifies access to the data in a camera calibration file."""

    def __init__(self, filename: str) -> None:
        """Load the file.

        Args:
            filename:  Path to the calibration YAML file.
        """
        self.filename = filename

        with open(filename) as file:
            self.data = yaml.safe_load(file)

    def __getitem__(self, name: str) -> Any:
        """Get the specified field from the calibration data.

        Array data is converted to numpy arrays, other fields are returned as is.
        """
        raw_data = self.data[name]
        if isinstance(raw_data, dict):
            return self.get_array(name)
        return raw_data

    def get_array(self, name: str) -> np.ndarray:
        """Get the specified array from the calibration data.

        Args:
            name:  Name of the array (e.g. "camera_matrix").

        Returns:
            The array with the specified name.
        """
        return config_to_array(self.data[name])
