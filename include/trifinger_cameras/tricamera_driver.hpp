/**
 * @file
 * @brief Wrapper on the Pylon Driver to synchronise three pylon dependent
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/pylon_driver.hpp>
#include <trifinger_cameras/tricamera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief Driver to create three instances of the PylonDriver
 * and get observations from them.
 */
class TriCameraDriver
    : public robot_interfaces::SensorDriver<TriCameraObservation>
{
public:
    /**
     * @param device_id_1 device user id of first camera
     * @param device_id_2 likewise, the 2nd's
     * @param device_id_3 and the 3rd's
     */
    TriCameraDriver(const std::string& device_id_1,
                    const std::string& device_id_2,
                    const std::string& device_id_3);

    /**
     * @brief Get the latest observation from the three cameras
     * @return TricameraObservation
     */
    TriCameraObservation get_observation();

private:
    PylonDriver cam_1, cam_2, cam_3;
};

}  // namespace trifinger_cameras
