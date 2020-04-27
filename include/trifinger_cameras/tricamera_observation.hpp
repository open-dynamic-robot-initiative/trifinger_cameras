/**
 * @file
 * @brief Defines the observation structure to be used for using
 * three pylon dependent cameras together.
 * @copyright 2020, New York University, Max Planck Gesellschaft. All rights
 *            reserved.
 * @license BSD 3-clause
 */

#pragma once

#include <trifinger_cameras/camera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief An array of three CameraObservation(s)
 */
struct TriCameraObservation
{
    typedef std::array<CameraObservation, 3> CameraArray;
    CameraArray cameras;
};

}  // namespace trifinger_cameras
