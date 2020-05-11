/**
 * @file
 * @brief Wrapper on the Pylon Driver to synchronise three pylon dependent
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/tricamera_driver.hpp>

namespace trifinger_cameras
{
TriCameraDriver::TriCameraDriver(const std::string& device_id_1,
                                 const std::string& device_id_2,
                                 const std::string& device_id_3)
    : cam_1(device_id_1), cam_2(device_id_2), cam_3(device_id_3)
{
}

TriCameraObservation TriCameraDriver::get_observation()
{
    TriCameraObservation tricam_obs;

    tricam_obs.cameras[0] = cam_1.get_observation();
    tricam_obs.cameras[1] = cam_2.get_observation();
    tricam_obs.cameras[2] = cam_3.get_observation();

    return tricam_obs;
}

}  // namespace trifinger_cameras

