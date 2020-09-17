/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2009, Willow Garage, Inc.
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

#include <Eigen/Eigen>
#include <sensor_msgs/distortion_models.h>
#include <yaml-cpp/yaml.h>
#include <boost/filesystem.hpp>
#include <cassert>
#include <cstring>
#include <ctime>
#include <fstream>

namespace trifinger_cameras
{

struct CameraParameters
{
    unsigned int image_width;
    unsigned int image_height;

    Eigen::Matrix3d camera_matrix;
    Eigen::Matrix<double, 5, 1> distortion_coefficients;

    Eigen::Matrix4d tf_world_to_camera;
};


static const char CAM_YML_NAME[] = "camera_name";
static const char WIDTH_YML_NAME[] = "image_width";
static const char HEIGHT_YML_NAME[] = "image_height";
static const char K_YML_NAME[] = "camera_matrix";
static const char D_YML_NAME[] = "distortion_coefficients";
static const char R_YML_NAME[] = "rectification_matrix";
static const char P_YML_NAME[] = "projection_matrix";
static const char DMODEL_YML_NAME[] = "distortion_model";

struct SimpleMatrix
{
    int rows;
    int cols;
    double* data;

    SimpleMatrix(int rows, int cols, double* data)
        : rows(rows), cols(cols), data(data)
    {
    }
};

template <typename T>
void operator>>(const YAML::Node& node, T& i)
{
    i = node.as<T>();
}

void operator>>(const YAML::Node& node, SimpleMatrix& m)
{
    int rows, cols;
    rows = node["rows"].as<int>();
    assert(rows == m.rows);
    cols = node["cols"].as<int>();
    assert(cols == m.cols);
    const YAML::Node& data = node["data"];
    for (int i = 0; i < rows * cols; ++i)
    {
        m.data[i] = data[i].as<double>();
    }
}

void operator>>(const YAML::Node& node, Eigen::Matrix3d& m)
{
    int rows, cols;
    rows = node["rows"].as<int>();
    assert(rows == m.rows());
    cols = node["cols"].as<int>();
    assert(cols == m.cols());
    const YAML::Node& data = node["data"];
    for (int i = 0; i < rows * cols; ++i)
    {
        int r = i / rows;
        int c = i - r * cols;
        m(r, c) = data[i].as<double>();
    }
}

/// \endcond

bool readCalibrationYml(std::istream& in,
                        std::string& camera_name,
                        sensor_msgs::CameraInfo& cam_info)
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
        doc[WIDTH_YML_NAME] >> cam_info.width;
        current_key = HEIGHT_YML_NAME;
        doc[HEIGHT_YML_NAME] >> cam_info.height;

        // Read in fixed-size matrices
        SimpleMatrix K_(3, 3, &cam_info.K[0]);
        current_key = K_YML_NAME;
        doc[K_YML_NAME] >> K_;

        // TODO: Disable rectification_matrix for now
        //SimpleMatrix R_(3, 3, &cam_info.R[0]);
        //current_key = R_YML_NAME;
        //doc[R_YML_NAME] >> R_;

        // TODO: Disable projection_matrix for now
        //SimpleMatrix P_(3, 4, &cam_info.P[0]);
        //current_key = P_YML_NAME;
        //doc[P_YML_NAME] >> P_;

        // Different distortion models may have different numbers of parameters
        current_key = DMODEL_YML_NAME;
        if (doc[DMODEL_YML_NAME])
        {
            doc[DMODEL_YML_NAME] >> cam_info.distortion_model;
        }
        else
        {
            // Assume plumb bob for backwards compatibility
            cam_info.distortion_model =
                sensor_msgs::distortion_models::PLUMB_BOB;
            std::cout << "WARNING: Camera calibration file did not specify "
                         "distortion model, "
                         "assuming plumb bob"
                      << std::endl;
        }
        current_key = D_YML_NAME;
        const YAML::Node& D_node = doc[D_YML_NAME];
        int D_rows, D_cols;
        D_node["rows"] >> D_rows;
        D_node["cols"] >> D_cols;
        const YAML::Node& D_data = D_node["data"];
        cam_info.D.resize(D_rows * D_cols);
        for (int i = 0; i < D_rows * D_cols; ++i) D_data[i] >> cam_info.D[i];

        return true;
    }
    catch (YAML::Exception& e)
    {
        std::cerr << "Exception parsing YAML camera calibration:\n"
                  << e.what() << std::endl;
        std::cerr << "Key causing the exception: " << current_key << std::endl;
        return false;
    }
}

bool readCalibrationYml(const std::string& file_name,
                        std::string& camera_name,
                        sensor_msgs::CameraInfo& cam_info)
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
