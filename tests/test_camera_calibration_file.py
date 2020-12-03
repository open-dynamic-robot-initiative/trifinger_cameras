#!/usr/bin/env python3
import os
import unittest
import numpy as np

from ament_index_python.packages import get_package_share_directory

from trifinger_cameras.camera_calibration_file import (
    config_to_array,
    CameraCalibrationFile,
)


class TestCameraCalibrationFile(unittest.TestCase):
    def test_config_to_array(self):
        config_row = {"rows": 1, "cols": 4, "data": [1, 2, 3, 4]}
        config_col = {"rows": 4, "cols": 1, "data": [1, 2, 3, 4]}
        config_mat = {
            "rows": 3,
            "cols": 4,
            "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        }

        np.testing.assert_array_equal(
            config_to_array(config_row), np.array([[1, 2, 3, 4]])
        )
        np.testing.assert_array_equal(
            config_to_array(config_col), np.array([[1], [2], [3], [4]])
        )
        np.testing.assert_array_equal(
            config_to_array(config_mat),
            np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]),
        )

    def test_file(self):
        file_path = os.path.join(
            get_package_share_directory("trifinger_cameras"),
            "tests",
            "camera_calib.yml",
        )

        ccf = CameraCalibrationFile(file_path)

        self.assertEquals(ccf.filename, file_path)

        np.testing.assert_array_equal(
            ccf["camera_matrix"],
            np.array(
                [[586.36, 0.0, 360.46], [0.0, 590.61, 286.55], [0.0, 0.0, 1.0]]
            ),
        )

        np.testing.assert_array_equal(
            ccf["distortion_coefficients"],
            np.array([[-0.2399, 0.0990, -0.0006, 0.0001, 0.0039]]),
        )


if __name__ == "__main__":
    unittest.main()
