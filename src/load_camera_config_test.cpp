#include <iostream>
#include <string>

#include <trifinger_cameras/parse_yml.h>
#include <sensor_msgs/msg/camera_info.hpp>

int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        std::cout << "Usage:  " << argv[0] << " <config_file>" << std::endl;
        exit(1);
    }

    std::string file = argv[1];
    std::string camera_name;
    sensor_msgs::msg::CameraInfo cam_info;
    trifinger_cameras::CameraParameters params;

    bool suc = trifinger_cameras::readCalibrationYml(file, camera_name, params);

    if (suc)
    {
        std::cout << "camera name: " << camera_name << std::endl;
        std::cout << params << std::endl;
    }
    else
    {
        std::cout << "Failure" << std::endl;
    }
}
