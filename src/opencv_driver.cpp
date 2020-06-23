/**
 * @file
 * @brief Driver to interface with the camera using OpenCV.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/opencv_driver.hpp>

#include <chrono>
#include <iostream>

#include <opencv2/opencv.hpp>

namespace trifinger_cameras
{
OpenCVDriver::OpenCVDriver(int device_id) : video_capture_(device_id)
{
}

CameraObservation OpenCVDriver::get_observation()
{
    if (!video_capture_.isOpened())
    {
        throw std::runtime_error("Could not access camera stream :(");
    }
    else
    {
        CameraObservation obs;

        video_capture_ >> obs.image;
        auto current_time = std::chrono::system_clock::now();
        obs.timestamp =
            std::chrono::duration<double>(current_time.time_since_epoch())
                .count();

        // make sure the image have the expected size
        if (obs.image.rows != obs.height || obs.image.cols != obs.width)
        {
            static bool printed_warning = false;
            if (!printed_warning)
            {
                std::cout << "WARNING: Size of captured image does not match "
                             "with expected observation.  Images are rescaled."
                          << std::endl;
                printed_warning = true;
            }
            cv::resize(obs.image, obs.image, cv::Size(obs.width, obs.height));
        }

        return obs;
    }
}
}  // namespace trifinger_cameras
