/**
 * @file
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include <ostream>
#include <string>

#include <Eigen/Eigen>

#include <serialization_utils/cereal_eigen.hpp>


namespace trifinger_cameras
{
struct CameraParameters
{
    unsigned int image_width;
    unsigned int image_height;

    Eigen::Matrix3d camera_matrix;
    Eigen::Matrix<double, 1, 5> distortion_coefficients;

    Eigen::Matrix4d tf_world_to_camera;

    template <class Archive>
    void serialize(Archive& archive)
    {
        archive(CEREAL_NVP(image_width),
                CEREAL_NVP(image_height),
                CEREAL_NVP(camera_matrix),
                CEREAL_NVP(distortion_coefficients),
                CEREAL_NVP(tf_world_to_camera));
    }

};

std::ostream& operator<<(std::ostream& os, const CameraParameters& cp);

struct CameraInfo: public CameraParameters
{
    float frame_rate_fps;

    template <class Archive>
    void serialize(Archive& archive)
    {
        CameraParameters::serialize(archive);
        archive(CEREAL_NVP(frame_rate_fps));
    }
};

}  // namespace trifinger_cameras
