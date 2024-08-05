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
class PylonDriver : public robot_interfaces::SensorDriver<CameraObservation>
{
public:
    /**
     * @param device_user_id "DeviceUserID" of the camera.
     * @param downsample_images If set to true (default), images are downsampled
     *     to half their original size.
     */
    PylonDriver(const std::string& device_user_id,
                bool downsample_images = true,
                Settings settings = Settings());

    ~PylonDriver();

    /**
     * @brief Downsample raw Bayer pattern by factor 2.
     *
     * Downsample a raw image by factor two, preserving the Bayer pattern.
     *
     * @param image Original image.
     *
     * @return Downsampled image.
     */
    static cv::Mat downsample_raw_image(const cv::Mat& image);

    /**
     * @brief Get the latest observation (image frame + timestamp of when the
     * frame's grabbed).
     * @return CameraObservation
     */
    CameraObservation get_observation();

private:
    std::shared_ptr<const PylonDriverSettings> settings_;
    std::string device_user_id_;
    const bool downsample_images_;
    Pylon::PylonAutoInitTerm auto_init_term_;
    Pylon::CInstantCamera camera_;
    Pylon::CImageFormatConverter format_converter_;

    void set_camera_configuration();
};

}  // namespace trifinger_cameras
