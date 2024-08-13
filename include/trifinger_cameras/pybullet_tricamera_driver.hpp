/**
 * @file
 * @brief TriCameraDriver for simulation (using rendered images)
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 */
#pragma once

#include <pybind11/embed.h>

#include <robot_interfaces/finger_types.hpp>
#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/camera_parameters.hpp>
#include <trifinger_cameras/settings.hpp>
#include <trifinger_cameras/tricamera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief Driver to get rendered camera images from pyBullet.
 */
class PyBulletTriCameraDriver
    : public robot_interfaces::SensorDriver<TriCameraObservation, TriCameraInfo>
{
public:
    PyBulletTriCameraDriver(
        robot_interfaces::TriFingerTypes::BaseDataPtr robot_data,
        bool render_images = true,
        Settings settings = Settings());

    // FIXME: Implement get_sensor_info()

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

    //! @brief If false, no images are rendered.  Images in observations will be
    //!        uninitialised.
    bool render_images_;

    //! @brief Pointer to robot data, needed for time synchronisation.
    robot_interfaces::TriFingerTypes::BaseDataPtr robot_data_;
    //! @brief Last robot time index at which a camera observation was returned.
    //         Needed for time synchronisation.
    time_series::Index last_update_robot_time_index_;

    //! Number of robot time steps after which the next frame should be fetched.
    int frame_rate_in_robot_steps_;
};

}  // namespace trifinger_cameras
