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

#include <pylon/PylonIncludes.h>

#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/camera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief Driver for interacting with a camera via Pylon and storing
 * images using OpenCV.
 */
class PylonDriver : public robot_interfaces::SensorDriver<CameraObservation>
{
public:

    /**
     * @param device_user_id_to_open The id of the camera device to open and
     * grab images from
     */
    PylonDriver(const std::string& device_user_id_to_open);

    ~PylonDriver();

    /**
     * @brief Get the latest observation (image frame + timestamp of when the
     * frame's grabbed).
     * @return CameraObservation
     */
    CameraObservation get_observation();

private:
    Pylon::PylonAutoInitTerm auto_init_term_;
    Pylon::CInstantCamera camera_;
    Pylon::CImageFormatConverter format_converter_;
    Pylon::CPylonImage pylon_image_;

    void set_camera_configuration(GenApi::INodeMap& nodemap);
};

}  // namespace trifinger_cameras
