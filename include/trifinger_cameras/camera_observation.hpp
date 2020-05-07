/**
 * @file
 * @brief Defines the observation structure to be used by any camera.
 * @copyright 2020, New York University, Max Planck Gesellschaft. All rights
 *            reserved.
 * @license BSD 3-clause
 */

#pragma once

#include <opencv2/opencv.hpp>
#include "cereal_cvmat.hpp"

namespace trifinger_cameras
{
/**
 * @brief Observation structure to store cv::Mat images with corresponding
 * timestamps.
 *
 */
struct CameraObservation
{
    cv::Mat image;
    double time_stamp;

    template <class Archive>
    void serialize(Archive& archive)
    {
        archive(image, time_stamp);
    }
};

}  // namespace trifinger_cameras
