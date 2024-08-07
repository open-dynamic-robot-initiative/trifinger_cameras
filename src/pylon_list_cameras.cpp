/**
 * @file
 * @brief Application to list all detected Pylon cameras
 */
#include <iostream>

// ignore warnings in the pylon headers
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
#include <pylon/PylonIncludes.h>
#pragma GCC diagnostic pop

int main()
{
    int ret = 0;
    try
    {
        Pylon::PylonInitialize();
        Pylon::CTlFactory& tl_factory = Pylon::CTlFactory::GetInstance();
        Pylon::DeviceInfoList_t device_list;

        if (tl_factory.EnumerateDevices(device_list) == 0)
        {
            std::cerr << "No cameras found." << std::endl;
        }
        else
        {
            Pylon::DeviceInfoList_t::const_iterator device_iterator;
            int i = 1;
            for (device_iterator = device_list.begin();
                 device_iterator != device_list.end();
                 ++i, ++device_iterator)
            {
                std::string camera_name(device_iterator->GetUserDefinedName());
                std::cout << i << ". " << camera_name << std::endl;
            }
        }
    }
    catch (const Pylon::GenericException& e)
    {
        std::cerr << "Camera Error: " << e.what() << std::endl;
        ret = 1;
    }
    Pylon::PylonTerminate();

    return ret;
}
