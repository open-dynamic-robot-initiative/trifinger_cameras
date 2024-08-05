#!/usr/bin/env python3
import unittest
import numpy as np
from scipy.spatial.transform import Rotation

from trifinger_cameras import utils


class TestUtils(unittest.TestCase):
    def test_rodrigues_to_matrix(self):
        rotvec = np.array([-0.87642918, 0.58070658, -1.62552038])
        mat = np.array(
            [
                [-0.07889507, 0.60004323, 0.79606764, 0.0],
                [-0.96862517, -0.23492755, 0.08108223, 0.0],
                [0.23567106, -0.76469417, 0.5997516, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        np.testing.assert_array_almost_equal(utils.rodrigues_to_matrix(rotvec), mat)

    def test_convert_image(self):
        # NOTE: this is not testing if the result is correct but simply uses
        # the result of an old call of the function to verify that the
        # behaviour did not change.

        raw_image = np.array(
            [
                [207, 206, 196, 107, 198, 204, 206],
                [199, 196, 175, 177, 182, 193, 201],
                [189, 85, 95, 175, 176, 108, 194],
                [40, 128, 83, 92, 92, 39, 64],
                [44, 64, 56, 89, 79, 60, 41],
                [69, 77, 64, 88, 66, 78, 73],
                [66, 69, 73, 78, 81, 82, 82],
            ],
            dtype=np.uint8,
        )

        img_bgr = np.array(
            [
                [
                    [196, 166, 172],
                    [196, 166, 172],
                    [187, 175, 146],
                    [177, 160, 166],
                    [185, 182, 187],
                    [193, 174, 194],
                    [193, 174, 194],
                ],
                [
                    [196, 166, 172],
                    [196, 166, 172],
                    [187, 175, 146],
                    [177, 160, 166],
                    [185, 182, 187],
                    [193, 174, 194],
                    [193, 174, 194],
                ],
                [
                    [162, 85, 142],
                    [162, 85, 142],
                    [148, 130, 95],
                    [135, 175, 136],
                    [125, 139, 176],
                    [116, 108, 185],
                    [116, 108, 185],
                ],
                [
                    [128, 68, 96],
                    [128, 68, 96],
                    [110, 83, 76],
                    [92, 110, 102],
                    [66, 92, 128],
                    [39, 81, 123],
                    [39, 81, 123],
                ],
                [
                    [103, 64, 50],
                    [103, 64, 50],
                    [96, 75, 56],
                    [90, 89, 68],
                    [74, 77, 79],
                    [59, 60, 60],
                    [59, 60, 60],
                ],
                [
                    [77, 67, 60],
                    [77, 67, 60],
                    [83, 64, 65],
                    [88, 74, 72],
                    [83, 66, 80],
                    [78, 70, 71],
                    [78, 70, 71],
                ],
                [
                    [77, 67, 60],
                    [77, 67, 60],
                    [83, 64, 65],
                    [88, 74, 72],
                    [83, 66, 80],
                    [78, 70, 71],
                    [78, 70, 71],
                ],
            ],
            dtype=np.uint8,
        )

        img_rgb = np.array(
            [
                [
                    [172, 166, 196],
                    [172, 166, 196],
                    [146, 175, 187],
                    [166, 160, 177],
                    [187, 182, 185],
                    [194, 174, 193],
                    [194, 174, 193],
                ],
                [
                    [172, 166, 196],
                    [172, 166, 196],
                    [146, 175, 187],
                    [166, 160, 177],
                    [187, 182, 185],
                    [194, 174, 193],
                    [194, 174, 193],
                ],
                [
                    [142, 85, 162],
                    [142, 85, 162],
                    [95, 130, 148],
                    [136, 175, 135],
                    [176, 139, 125],
                    [185, 108, 116],
                    [185, 108, 116],
                ],
                [
                    [96, 68, 128],
                    [96, 68, 128],
                    [76, 83, 110],
                    [102, 110, 92],
                    [128, 92, 66],
                    [123, 81, 39],
                    [123, 81, 39],
                ],
                [
                    [50, 64, 103],
                    [50, 64, 103],
                    [56, 75, 96],
                    [68, 89, 90],
                    [79, 77, 74],
                    [60, 60, 59],
                    [60, 60, 59],
                ],
                [
                    [60, 67, 77],
                    [60, 67, 77],
                    [65, 64, 83],
                    [72, 74, 88],
                    [80, 66, 83],
                    [71, 70, 78],
                    [71, 70, 78],
                ],
                [
                    [60, 67, 77],
                    [60, 67, 77],
                    [65, 64, 83],
                    [72, 74, 88],
                    [80, 66, 83],
                    [71, 70, 78],
                    [71, 70, 78],
                ],
            ],
            dtype=np.uint8,
        )

        img_gray = np.array(
            [
                [171, 171, 167, 164, 184, 182, 182],
                [171, 171, 167, 164, 184, 182, 182],
                [111, 111, 121, 159, 149, 132, 132],
                [83, 83, 84, 105, 100, 89, 89],
                [64, 64, 72, 83, 77, 60, 60],
                [66, 66, 66, 75, 72, 71, 71],
                [66, 66, 66, 75, 72, 71, 71],
            ],
            dtype=np.uint8,
        )

        np.testing.assert_array_equal(utils.convert_image(raw_image), img_bgr)
        np.testing.assert_array_equal(utils.convert_image(raw_image, "bgr"), img_bgr)
        np.testing.assert_array_equal(utils.convert_image(raw_image, "rgb"), img_rgb)
        np.testing.assert_array_equal(utils.convert_image(raw_image, "gray"), img_gray)

        # verify that invalid formats result in an error
        with self.assertRaises(ValueError):
            utils.convert_image(raw_image, "foo")


if __name__ == "__main__":
    unittest.main()
