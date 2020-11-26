/**
 * @file
 * @brief TriCameraDriver for simulation (using rendered images)
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 */
#pragma once

#include <pybind11/embed.h>

#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/tricamera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief Driver to get rendered camera images from pyBullet.
 */
class PyBulletTriCameraDriver : public robot_interfaces::SensorDriver<
                                    trifinger_cameras::TriCameraObservation>
{
public:
    PyBulletTriCameraDriver();

    /**
     * @brief Get the latest observation from the three cameras
     * @return TricameraObservation
     */
    trifinger_cameras::TriCameraObservation get_observation();

private:
    //! @brief Python object to access cameras in pyBullet.
    pybind11::object cameras_;

    //! @brief The numpy module.
    pybind11::module numpy_;
};

}  // namespace trifinger_cameras

