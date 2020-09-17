/**
 * @file
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include <Eigen/Eigen>
#include <ostream>

namespace trifinger_cameras
{
struct CameraParameters
{
    unsigned int image_width;
    unsigned int image_height;

    Eigen::Matrix3d camera_matrix;
    Eigen::Matrix<double, 5, 1> distortion_coefficients;

    Eigen::Matrix4d tf_world_to_camera;
};

std::ostream& operator<<(std::ostream& os, const CameraParameters& cp);

}  // namespace trifinger_cameras
