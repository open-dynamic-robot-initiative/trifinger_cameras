/**
 * @file
 * @brief Driver to interface with the camera using OpenCV.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include <robot_interfaces/sensors/sensor_driver.hpp>
#include <trifinger_cameras/camera_observation.hpp>
#include <trifinger_cameras/camera_parameters.hpp>

namespace trifinger_cameras
{
/**
 * @brief Driver for interacting with any camera using OpenCV.
 */
class OpenCVDriver
    : public robot_interfaces::SensorDriver<CameraObservation, CameraInfo>
{
public:
    OpenCVDriver(int device_id);

    /**
     * @brief Grab a single frame along with its timestamp.
     *
     * @return Image frame consisting of an image matrix and the time at
     * which it was grabbed.
     */
    CameraObservation get_observation();

private:
    cv::VideoCapture video_capture_;
};

}  // namespace trifinger_cameras
