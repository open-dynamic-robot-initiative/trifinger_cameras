/**
 * @file
 * @brief Wrapper on the Pylon Driver to synchronise three pylon dependent
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include <array>
#include <chrono>
#include <filesystem>
#include <string>

#include <cereal/types/array.hpp>

#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/camera_parameters.hpp>
#include <trifinger_cameras/pylon_driver.hpp>
#include <trifinger_cameras/tricamera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief Driver to create three instances of the PylonDriver
 * and get observations from them.
 */
class TriCameraDriver
    : public robot_interfaces::SensorDriver<TriCameraObservation, TriCameraInfo>
{
public:
    //! @brief Rate at which images are acquired.
    std::chrono::milliseconds rate;

    /**
     * @param device_id_1 device user id of first camera
     * @param device_id_2 likewise, the 2nd's
     * @param device_id_3 and the 3rd's
     * @param downsample_images Not supported anymore.  Must be to ``false``.
     * @param settings Settings for the cameras.
     */
    TriCameraDriver(const std::string& device_id_1,
                    const std::string& device_id_2,
                    const std::string& device_id_3,
                    bool downsample_images = false,
                    Settings settings = Settings());

    /**
     * @param camera_calibration_file_1 Calibration file of first camera
     * @param camera_calibration_file_2 likewise, the 2nd's
     * @param camera_calibration_file_3 and the 3rd's
     * @param downsample_images Not supported anymore.  Must be to ``false``.
     * @param settings Settings for the cameras.
     */
    TriCameraDriver(const std::filesystem::path& camera_calibration_file_1,
                    const std::filesystem::path& camera_calibration_file_2,
                    const std::filesystem::path& camera_calibration_file_3,
                    bool downsample_images = false,
                    Settings settings = Settings());

    /**
     * @brief Get the camera parameters (image size and calibration
     * coefficients).
     *
     * **Important:**  The calibration coefficients are only set if the driver
     * is initialized with calibration files (see constructor).  Otherwise,
     * they will be all zero.
     */
    TriCameraInfo get_sensor_info() override;

    /**
     * @brief Get the latest observation from the three cameras
     * @return TricameraObservation
     */
    TriCameraObservation get_observation() override;

private:
    std::chrono::time_point<std::chrono::system_clock> last_update_time_;
    PylonDriver camera1_, camera2_, camera3_;
    TriCameraInfo sensor_info_ = {};

    void init(Settings settings);
};

}  // namespace trifinger_cameras
