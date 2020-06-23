/**
 * @file
 * @brief Defines the observation structure to be used for using
 * three pylon dependent cameras together.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include "camera_observation.hpp"

namespace trifinger_cameras
{
/**
 * @brief An array of three CameraObservation(s)
 */
struct TriCameraObservation
{
    std::array<CameraObservation, 3> cameras;

    template <class Archive>
    void serialize(Archive& archive)
    {
        archive(cameras);
    }
};

}  // namespace trifinger_cameras
