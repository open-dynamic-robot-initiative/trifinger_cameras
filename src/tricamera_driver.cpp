/**
 * @file
 * @brief Wrapper on the Pylon Driver to synchronise three pylon dependent
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/settings.hpp>
#include <trifinger_cameras/tricamera_driver.hpp>

#include <thread>

namespace trifinger_cameras
{
TriCameraDriver::TriCameraDriver(const std::string& device_id_1,
                                 const std::string& device_id_2,
                                 const std::string& device_id_3,
                                 bool downsample_images,
                                 Settings settings)
    : last_update_time_(std::chrono::system_clock::now()),
      camera1_(device_id_1, downsample_images, settings),
      camera2_(device_id_2, downsample_images, settings),
      camera3_(device_id_3, downsample_images, settings)
{
    init(settings);
}

TriCameraDriver::TriCameraDriver(
    const std::filesystem::path& camera_calibration_file_1,
    const std::filesystem::path& camera_calibration_file_2,
    const std::filesystem::path& camera_calibration_file_3,
    bool downsample_images,
    Settings settings)

    : last_update_time_(std::chrono::system_clock::now()),
      camera1_(camera_calibration_file_1, downsample_images, settings),
      camera2_(camera_calibration_file_2, downsample_images, settings),
      camera3_(camera_calibration_file_3, downsample_images, settings)
{
    init(settings);
}

TriCameraInfo TriCameraDriver::get_sensor_info()
{
    return sensor_info_;
}

TriCameraObservation TriCameraDriver::get_observation()
{
    last_update_time_ += this->rate;
    std::this_thread::sleep_until(last_update_time_);

    TriCameraObservation tricam_obs;

    tricam_obs.cameras[0] = camera1_.get_observation();
    tricam_obs.cameras[1] = camera2_.get_observation();
    tricam_obs.cameras[2] = camera3_.get_observation();

    return tricam_obs;
}

void TriCameraDriver::init(Settings settings)
{
    auto cfg = settings.get_tricamera_driver_settings();
    float rate_sec = 1.f / cfg->frame_rate_fps;
    rate = std::chrono::milliseconds(std::lround(rate_sec * 1000));

    sensor_info_ = TriCameraInfo(camera1_.get_sensor_info(),
                                 camera2_.get_sensor_info(),
                                 camera3_.get_sensor_info());
    sensor_info_.camera[0].frame_rate_fps = cfg->frame_rate_fps;
    sensor_info_.camera[1].frame_rate_fps = cfg->frame_rate_fps;
    sensor_info_.camera[2].frame_rate_fps = cfg->frame_rate_fps;
}

}  // namespace trifinger_cameras
