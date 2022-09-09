/**
 * @file
 * @brief Driver to interface with the camera using Pylon.
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/pylon_driver.hpp>

#include <chrono>
#include <iostream>

#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <opencv2/opencv.hpp>

namespace trifinger_cameras
{
/**
 * @brief Convert BGR image to BayerBG pattern.
 *
 * Reconstruct a BayerBG pattern from the given BGR image.
 *
 * @param bgr_image Input image in BGR format.
 *
 * @return Image in BayerBG format.
 */
cv::Mat BGR2BayerBG(const cv::Mat& bgr_image)
{
    // channel names, assuming input is BGR
    constexpr int CHANNEL_RED = 2;
    constexpr int CHANNEL_GREEN = 1;
    constexpr int CHANNEL_BLUE = 0;

    // channel map to get the following pattern (called "BG" in OpenCV):
    //
    //   R G
    //   G B
    //
    constexpr int channel_map[2][2] = {{CHANNEL_RED, CHANNEL_GREEN},
                                       {CHANNEL_GREEN, CHANNEL_BLUE}};

    cv::Mat bayer_img(bgr_image.rows, bgr_image.cols, CV_8UC1);
    for (int r = 0; r < bgr_image.rows; r++)
    {
        for (int c = 0; c < bgr_image.cols; c++)
        {
            int channel = channel_map[r % 2][c % 2];

            bayer_img.at<uint8_t>(r, c) =
                bgr_image.at<cv::Vec3b>(r, c)[channel];
        }
    }

    return bayer_img;
}

PylonDriver::PylonDriver(const std::string& device_user_id,
                         bool downsample_images)
    : device_user_id_(device_user_id), downsample_images_(downsample_images)
{
    auto logger = spdlog::stderr_color_mt("PylonDriver");

    logger->info("Open Pylon camera {}", device_user_id);

    try
    {
        logger->debug("Create Pylon::CTlFactory");
        Pylon::CTlFactory& tl_factory = Pylon::CTlFactory::GetInstance();
        logger->debug("PylonInitialize");
        Pylon::PylonInitialize();
        Pylon::DeviceInfoList_t device_list;

        logger->debug("Check devices.");
        if (tl_factory.EnumerateDevices(device_list) == 0)
        {
            Pylon::PylonTerminate();
            throw std::runtime_error("No devices present, please connect one.");
        }

        Pylon::DeviceInfoList_t::const_iterator device_iterator;
        if (device_user_id.empty())
        {
            device_iterator = device_list.begin();
            camera_.Attach(tl_factory.CreateDevice(*device_iterator));
            logger->warn(
                "No device ID specified. Creating a camera object "
                "with the first device in the device list ({}).",
                device_iterator->GetUserDefinedName());
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
                    logger->debug("Found Pylon camera {}", device_user_id);
                    found_desired_device = true;
                    break;
                }
            }

            if (found_desired_device)
            {
                logger->debug("Create device");
                camera_.Attach(tl_factory.CreateDevice(*device_iterator));
            }
            else
            {
                Pylon::PylonTerminate();
                throw std::runtime_error(
                    "Device id " + device_user_id_ +
                    " doesn't correspond to any "
                    "connected devices, please retry with a valid id.");
            }

            logger->debug("Open camera");
            camera_.Open();
            camera_.MaxNumBuffer = 5;

            logger->debug("Configure camera");
            set_camera_configuration();

            logger->info("Start grabbing images");
            camera_.StartGrabbing(Pylon::GrabStrategy_LatestImageOnly);
        }

        format_converter_.OutputPixelFormat = Pylon::PixelType_BGR8packed;
    }
    catch (const Pylon::GenericException& e)
    {
        // convert Pylon exceptions to an std exception, so it is understood by
        // pybind11
        throw std::runtime_error("Camera Error (" + device_user_id_ +
                                 "): " + e.what());
    }
}

PylonDriver::~PylonDriver()
{
    spdlog::stderr_color_mt("PylonDriver")->info("Disconnect camera.");
    camera_.StopGrabbing();
    Pylon::PylonTerminate();
}

CameraObservation PylonDriver::get_observation()
{
    CameraObservation image_frame;
    Pylon::CGrabResultPtr ptr_grab_result;

    try
    {
        // FIXME 5second timeout?
        camera_.RetrieveResult(
            5000, ptr_grab_result, Pylon::TimeoutHandling_ThrowException);
        auto current_time = std::chrono::system_clock::now();
        image_frame.timestamp =
            std::chrono::duration<double>(current_time.time_since_epoch())
                .count();

        if (ptr_grab_result->GrabSucceeded())
        {
            // ensure that the actual image size matches with the expected one
            if (ptr_grab_result->GetHeight() / 2 != image_frame.height ||
                ptr_grab_result->GetWidth() / 2 != image_frame.width)
            {
                std::stringstream msg;
                msg << device_user_id_ << ": "
                    << "Size of grabbed frame (" << ptr_grab_result->GetWidth()
                    << "x" << ptr_grab_result->GetHeight()
                    << ") does not match expected size ("
                    << image_frame.width * 2 << "x" << image_frame.height * 2
                    << ").";

                throw std::length_error(msg.str());
            }

            if (downsample_images_)
            {
                Pylon::CPylonImage pylon_image_bgr;
                format_converter_.Convert(pylon_image_bgr, ptr_grab_result);

                // NOTE: the cv::Mat points to the memory of pylon_image_bgr!
                cv::Mat image_bgr =
                    cv::Mat(ptr_grab_result->GetHeight(),
                            ptr_grab_result->GetWidth(),
                            CV_8UC3,
                            (uint8_t*)pylon_image_bgr.GetBuffer());

                // remove a bit of noise
                cv::medianBlur(image_bgr, image_bgr, 3);

                // resize image
                constexpr float DOWNSAMPLING_FACTOR = 0.5;
                cv::resize(image_bgr,
                           image_bgr,
                           cv::Size(),
                           DOWNSAMPLING_FACTOR,
                           DOWNSAMPLING_FACTOR,
                           cv::INTER_LINEAR);

                // convert back to BayerBG to not break the API
                image_frame.image = BGR2BayerBG(image_bgr);
            }
            else
            {
                // NOTE: the cv::Mat points to the memory of pylon_image!
                cv::Mat image = cv::Mat(ptr_grab_result->GetHeight(),
                                        ptr_grab_result->GetWidth(),
                                        CV_8UC1,
                                        (uint8_t*)ptr_grab_result->GetBuffer());

                image_frame.image = image.clone();
            }
        }
        else
        {
            throw std::runtime_error("Failed to grab image from camera " +
                                     device_user_id_ + ".");
        }
    }
    catch (const Pylon::GenericException& e)
    {
        // convert Pylon exceptions to an std exception, so it is understood by
        // pybind11
        throw std::runtime_error("Camera Error (" + device_user_id_ +
                                 "): " + e.what());
    }

    return image_frame;
}

cv::Mat PylonDriver::downsample_raw_image(const cv::Mat& image)
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

            downsampled.at<uint8_t>(r, c) = image.at<uint8_t>(r2, c2);
            downsampled.at<uint8_t>(r + 1, c) = image.at<uint8_t>(r2 + 1, c2);
            downsampled.at<uint8_t>(r, c + 1) = image.at<uint8_t>(r2, c2 + 1);
            downsampled.at<uint8_t>(r + 1, c + 1) =
                image.at<uint8_t>(r2 + 1, c2 + 1);
        }
    }

    return downsampled;
}

void PylonDriver::set_camera_configuration()
{
    const std::string filename =
        ament_index_cpp::get_package_share_directory("trifinger_cameras") +
        "/config/pylon_camera_settings.txt";

    Pylon::CFeaturePersistence::Load(
        filename.c_str(), &camera_.GetNodeMap(), true);

    // Use the following command to generate a config file with the current
    // settings:
    // Pylon::CFeaturePersistence::Save("/tmp/camera_settings.txt",
    //                                 &camera_.GetNodeMap());
}
}  // namespace trifinger_cameras
