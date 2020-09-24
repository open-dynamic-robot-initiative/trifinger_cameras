/**
 * @file
 * @brief Driver to interface with the camera using Pylon.
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/pylon_driver.hpp>

#include <chrono>
#include <iostream>

#include <ros/package.h>
#include <opencv2/opencv.hpp>

namespace trifinger_cameras
{
PylonDriver::PylonDriver(const std::string& device_user_id,
                         bool downsample_images)
    : downsample_images_(downsample_images)
{
    Pylon::CTlFactory& tl_factory = Pylon::CTlFactory::GetInstance();
    Pylon::PylonInitialize();
    Pylon::DeviceInfoList_t device_list;

    if (tl_factory.EnumerateDevices(device_list) == 0)
    {
        Pylon::PylonTerminate();
        throw std::runtime_error("No devices present, please connect one.");
    }

    else
    {
        Pylon::DeviceInfoList_t::const_iterator device_iterator;
        if (device_user_id.empty())
        {
            device_iterator = device_list.begin();
            camera_.Attach(tl_factory.CreateDevice(*device_iterator));
            std::cout << "No device ID specified. Creating a camera object "
                         "with the first device id in the device list."
                      << std::endl;
        }
        else
        {
            bool found_desired_device = false;

            for (device_iterator = device_list.begin();
                 device_iterator != device_list.end();
                 ++device_iterator)
            {
                std::string device_user_id_found(
                    device_iterator->GetUserDefinedName());
                if (device_user_id == device_user_id_found)
                {
                    found_desired_device = true;
                    break;
                }
            }

            if (found_desired_device)
            {
                camera_.Attach(tl_factory.CreateDevice(*device_iterator));
            }
            else
            {
                Pylon::PylonTerminate();
                throw std::runtime_error(
                    "Device id specified doesn't correspond to any "
                    "connected devices, please retry with a valid id.");
            }

            camera_.Open();
            camera_.MaxNumBuffer = 5;

            set_camera_configuration(camera_.GetNodeMap());

            camera_.StartGrabbing(Pylon::GrabStrategy_LatestImageOnly);
        }
    }
}

PylonDriver::~PylonDriver()
{
    camera_.StopGrabbing();
    Pylon::PylonTerminate();
}

CameraObservation PylonDriver::get_observation()
{
    CameraObservation image_frame;
    Pylon::CGrabResultPtr ptr_grab_result;

    // FIXME 5second timeout?
    camera_.RetrieveResult(
        5000, ptr_grab_result, Pylon::TimeoutHandling_ThrowException);
    auto current_time = std::chrono::system_clock::now();
    image_frame.timestamp =
        std::chrono::duration<double>(current_time.time_since_epoch()).count();

    if (ptr_grab_result->GrabSucceeded())
    {
        // ensure that the actual image size matches with the expected one
        if (ptr_grab_result->GetHeight() / 2 != image_frame.height ||
            ptr_grab_result->GetWidth() / 2 != image_frame.width)
        {
            std::stringstream msg;
            msg << "Size of grabbed frame (" << ptr_grab_result->GetWidth()
                << "x" << ptr_grab_result->GetHeight()
                << ") does not match expected size (" << image_frame.width * 2
                << "x" << image_frame.height * 2 << ").";

            throw std::length_error(msg.str());
        }

        // NOTE: If created like this, the cv::Mat points to the memory of
        // pylon_image!
        cv::Mat image = cv::Mat(ptr_grab_result->GetHeight(),
                                ptr_grab_result->GetWidth(),
                                CV_8UC1,
                                (uint8_t*)ptr_grab_result->GetBuffer());

        if (downsample_images_)
        {
            // Downsample resolution by factor 2.  We are operating on the raw
            // image here, so we need to be careful to preserve the Bayer
            // pattern. This is done by iterating in steps of 4 over the
            // original image, keeping the first two rows/columns and discarding
            // the second two.
            image_frame.image = downsample_raw_image(image);
        }
        else
        {
            image_frame.image = image.clone();
        }
    }
    else
    {
        throw std::runtime_error("Failed to access images from the camera.");
    }

    return image_frame;
}

cv::Mat PylonDriver::downsample_raw_image(const cv::Mat &image)
{
    // Downsample resolution by factor 2.  We are operating on the raw
    // image here, so we need to be careful to preserve the Bayer
    // pattern. This is done by iterating in steps of 4 over the
    // original image, keeping the first two rows/columns and discarding
    // the second two.
    cv::Mat downsampled(image.cols / 2, image.rows / 2, CV_8UC1);
    for (int r = 0; r < downsampled.rows; r += 2)
    {
        for (int c = 0; c < downsampled.cols; c += 2)
        {
            int r2 = r * 2;
            int c2 = c * 2;

            downsampled.at<uint8_t>(r, c) =
                image.at<uint8_t>(r2, c2);
            downsampled.at<uint8_t>(r + 1, c) =
                image.at<uint8_t>(r2 + 1, c2);
            downsampled.at<uint8_t>(r, c + 1) =
                image.at<uint8_t>(r2, c2 + 1);
            downsampled.at<uint8_t>(r + 1, c + 1) =
                image.at<uint8_t>(r2 + 1, c2 + 1);
        }
    }

    return downsampled;
}

void PylonDriver::set_camera_configuration(GenApi::INodeMap& nodemap)
{
    const std::string filename = ros::package::getPath("trifinger_cameras") +
                                 "/config/pylon_camera_settings.txt";
    Pylon::CFeaturePersistence::Load(
        filename.c_str(), &camera_.GetNodeMap(), true);

    // Use the following command to generate a config file with the current
    // settings:
    // Pylon::CFeaturePersistence::Save("/tmp/camera_settings.txt",
    //                                 &camera_.GetNodeMap());
}
}  // namespace trifinger_cameras
