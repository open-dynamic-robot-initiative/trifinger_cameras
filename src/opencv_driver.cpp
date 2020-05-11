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
OpenCVDriver::OpenCVDriver(int device_id)
{
    cv::VideoCapture cap(device_id);
    video_capture_ = cap;
}

CameraObservation OpenCVDriver::get_observation()
{
    if (!video_capture_.isOpened())
    {
        throw std::runtime_error("Could not access camera stream :(");
    }
    else
    {
#ifdef VERBOSE
        std::cout << "Succeeded in accessing camera stream!" << std::endl;
#endif
        CameraObservation image_frame;
        cv::Mat frame;
        auto current_time = std::chrono::system_clock::now();

        video_capture_ >> frame;
        image_frame.image = frame;
        image_frame.time_stamp =
            std::chrono::duration<double>(current_time.time_since_epoch())
                .count();
        return image_frame;
    }
}
}  // namespace trifinger_cameras
