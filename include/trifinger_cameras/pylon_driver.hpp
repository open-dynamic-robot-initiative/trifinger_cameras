/**
 * @file
 * @brief Driver to interface with the camera using Pylon.
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 *
 * References-
 * https://www.baslerweb.com/en/sales-support/downloads/document-downloads/pylon-sdk-samples-manual/
 * https://github.com/basler/pylon-ros-camera/blob/9f3832127fc39a2c181cbeb5257054352e2ef7fe/pylon_camera/src/pylon_camera/pylon_camera.cpp#L132
 *
 */
#pragma once

#include <filesystem>

#ifndef Pylon_FOUND
#error Cannot use PylonDriver without Pylon.
#endif

// ignore warnings in the pylon headers
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#include <pylon/PylonIncludes.h>
#pragma GCC diagnostic pop

#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/camera_observation.hpp>
#include <trifinger_cameras/camera_parameters.hpp>
#include <trifinger_cameras/settings.hpp>

namespace trifinger_cameras
{
/**
 * @brief Connect to Pylon camera.
 *
 * @param device_user_id The user-defined name of the camera.  Can be set with
 *  the executable `pylon_write_device_user_id_to_camera`.  Pass empty string to
 *  simply connect to the first camera found.
 * @param camera Pointer to the Pylon::CInstantCamera instance to which the
 *  camera will be attached.
 */
void pylon_connect(std::string_view device_user_id,
                   Pylon::CInstantCamera* camera);

/**
 * @brief Driver for interacting with a camera via Pylon and storing
 * images using OpenCV.
 */
class PylonDriver
    : public robot_interfaces::SensorDriver<CameraObservation, CameraInfo>
{
public:
    /**
     * @brief Connect to camera based on name.
     *
     * When using this constructor, the camera calibration coefficients returned
     * by @ref get_sensor_info will be set to zero.
     *
     * @param device_user_id "DeviceUserID" of the camera.  Pass empty string to
     * connect to first camera found (useful if only one camera is connected).
     * @param downsample_images Not supported anymore.  Must be to ``false``.
     * @param settings Settings for the camera.
     */
    PylonDriver(const std::string& device_user_id,
                bool downsample_images = false,
                Settings settings = Settings());

    /**
     * @brief Connect to camera based on calibration file.
     *
     * The provided calibration file is expected to be in YAML format and
     * contain the "camera_name" (= DeviceUserID) as well as calibration
     * coefficients.  The latter will be used in the CameraInfo returned by @ref
     * get_sensor_info.
     *
     * @param camera_calibration_file Path to the camera calibration file.
     * @param downsample_images Not supported anymore.  Must be to ``false``.
     * @param settings Settings for the camera.
     */
    PylonDriver(const std::filesystem::path& camera_calibration_file,
                bool downsample_images = false,
                Settings settings = Settings());

    ~PylonDriver();

    /**
     * @brief Get the camera parameters (image size and calibration
     * coefficients).
     *
     * **Important:**  The calibration coefficients are only set if the driver
     * is initialized with a calibration file (see constructor).  Otherwise,
     * they will be empty.
     */
    virtual CameraInfo get_sensor_info() override;

    /**
     * @brief Get the latest observation (image frame + timestamp of when the
     * frame's grabbed).
     * @return CameraObservation
     */
    virtual CameraObservation get_observation() override;

private:
    std::shared_ptr<const PylonDriverSettings> settings_;
    trifinger_cameras::CameraInfo camera_info_ = {};
    std::string device_user_id_;
    Pylon::PylonAutoInitTerm auto_init_term_;
    Pylon::CInstantCamera camera_;
    Pylon::CImageFormatConverter format_converter_;

    /**
     * @brief Base constructor to be called by public constructors.
     * @param downsample_images Not supported anymore.  Must be to ``false``.
     * @param settings Settings for the camera.
     */
    PylonDriver(bool downsample_images, Settings settings);

    //! Initialize the camera connection (to be called in the constructor).
    void init(const std::string& device_user_id);

    void set_camera_configuration();
};

}  // namespace trifinger_cameras
