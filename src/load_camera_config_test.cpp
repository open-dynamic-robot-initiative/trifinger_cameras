#include <trifinger_cameras/parse_yml.h>
#include <sensor_msgs/CameraInfo.h>


int main(int argc, char* argv[])
{
    std::string file = argv[1];
    std::string camera_name;
    sensor_msgs::CameraInfo cam_info;

    bool suc = trifinger_cameras::readCalibrationYml(file, camera_name, cam_info);

    if (suc)
    {
        std::cout << "camera name: " << camera_name << std::endl;
        std::cout << cam_info << std::endl;
    }
    else
    {
        std::cout << "Failure" << std::endl;
    }
}
