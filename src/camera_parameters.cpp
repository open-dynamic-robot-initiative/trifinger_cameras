/**
 * @file
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/camera_parameters.hpp>

namespace trifinger_cameras
{
std::ostream& operator<<(std::ostream& os, const CameraParameters& cp)
{
    os << "CameraParameters:" << std::endl
       << "image_width: " << cp.image_width << std::endl
       << "image_height: " << cp.image_height << std::endl
       << "distortion_coefficients: " << cp.distortion_coefficients << std::endl
       << "camera_matrix:" << std::endl
       << cp.camera_matrix << std::endl
       << "tf_world_to_camera:" << std::endl
       << cp.tf_world_to_camera << std::endl;
    return os;
}
}  // namespace trifinger_cameras
