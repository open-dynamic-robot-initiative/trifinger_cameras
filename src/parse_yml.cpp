/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2009, Willow Garage, Inc.
 *  Copyright (c) 2020, Max Planck Gesellschaft
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of the Willow Garage nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *********************************************************************/

#include <trifinger_cameras/parse_yml.h>

#include <yaml-cpp/yaml.h>
#include <cassert>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iostream>

namespace trifinger_cameras
{
static const char CAM_YML_NAME[] = "camera_name";
static const char WIDTH_YML_NAME[] = "image_width";
static const char HEIGHT_YML_NAME[] = "image_height";
static const char K_YML_NAME[] = "camera_matrix";
static const char D_YML_NAME[] = "distortion_coefficients";
static const char R_YML_NAME[] = "rectification_matrix";
static const char P_YML_NAME[] = "projection_matrix";
static const char DMODEL_YML_NAME[] = "distortion_model";

template <typename T>
void operator>>(const YAML::Node& node, T& i)
{
    i = node.as<T>();
}

template <typename T>
void yaml_to_eigen(const YAML::Node& node, T& m)
{
    int rows, cols;

    rows = node["rows"].as<int>();
    if (rows != m.rows())
    {
        throw std::runtime_error("Invalid number of rows. Expected " +
                                 std::to_string(rows) + ", got " +
                                 std::to_string(m.rows()));
    }
    cols = node["cols"].as<int>();
    if (cols != m.cols())
    {
        throw std::runtime_error("Invalid number of cols. Expected " +
                                 std::to_string(cols) + ", got " +
                                 std::to_string(m.cols()));
    }

    const YAML::Node& data = node["data"];
    for (int i = 0; i < rows * cols; ++i)
    {
        int r = i / cols;
        int c = i % cols;
        m(r, c) = data[i].as<double>();
    }
}

void operator>>(const YAML::Node& node, Eigen::Matrix3d& m)
{
    yaml_to_eigen(node, m);
}

void operator>>(const YAML::Node& node, Eigen::Matrix4d& m)
{
    yaml_to_eigen(node, m);
}

void operator>>(const YAML::Node& node, Eigen::Matrix<double, 1, 5>& m)
{
    yaml_to_eigen(node, m);
}

/// \endcond

bool readCalibrationYml(std::istream& in,
                        std::string& camera_name,
                        CameraParameters& cam_info)
{
    std::string current_key = "none";
    try
    {
        YAML::Node doc = YAML::Load(in);

        current_key = CAM_YML_NAME;
        if (doc[CAM_YML_NAME])
            doc[CAM_YML_NAME] >> camera_name;
        else
            camera_name = "unknown";

        current_key = WIDTH_YML_NAME;
        doc[WIDTH_YML_NAME] >> cam_info.image_width;
        current_key = HEIGHT_YML_NAME;
        doc[HEIGHT_YML_NAME] >> cam_info.image_height;

        // Read in fixed-size matrices
        current_key = K_YML_NAME;
        doc[K_YML_NAME] >> cam_info.camera_matrix;

        current_key = D_YML_NAME;
        doc[D_YML_NAME] >> cam_info.distortion_coefficients;

        current_key = "tf_world_to_camera";
        doc["tf_world_to_camera"] >> cam_info.tf_world_to_camera;

        // TODO: Disable rectification_matrix for now
        // SimpleMatrix R_(3, 3, &cam_info.R[0]);
        // current_key = R_YML_NAME;
        // doc[R_YML_NAME] >> R_;

        // TODO: Disable projection_matrix for now
        // SimpleMatrix P_(3, 4, &cam_info.P[0]);
        // current_key = P_YML_NAME;
        // doc[P_YML_NAME] >> P_;

        return true;
    }
    catch (std::exception& e)
    {
        std::cerr << "Exception parsing YAML camera calibration:\n"
                  << e.what() << std::endl;
        std::cerr << "Key causing the exception: " << current_key << std::endl;
        return false;
    }
}

bool readCalibrationYml(const std::string& file_name,
                        std::string& camera_name,
                        CameraParameters& cam_info)
{
    std::ifstream fin(file_name.c_str());
    if (!fin.good())
    {
        std::cerr << "ERROR: Unable to open camera calibration file "
                  << file_name.c_str() << std::endl;
        return false;
    }
    bool success = readCalibrationYml(fin, camera_name, cam_info);
    if (!success)
        std::cerr << "ERROR: Failed to parse camera calibration from file"
                  << file_name.c_str() << std::endl;
    return success;
}

}  // namespace trifinger_cameras
