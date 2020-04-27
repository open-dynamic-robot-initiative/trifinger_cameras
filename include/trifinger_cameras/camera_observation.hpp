/**
 * @file
 * @brief Defines the observation structure to be used by any camera.
 * @copyright 2020, New York University, Max Planck Gesellschaft. All rights
 *            reserved.
 * @license BSD 3-clause
 */

#pragma once

#include <opencv2/opencv.hpp>

namespace trifinger_cameras
{
/**
 * @brief Observation structure to store cv::Mat images with corresponding
 * timestamps.
 *
 */
struct CameraObservation
{
    typedef cv::Mat Image;
    typedef double TimeStamp;
    Image image;
    TimeStamp time_stamp;
};

}  // namespace trifinger_cameras
