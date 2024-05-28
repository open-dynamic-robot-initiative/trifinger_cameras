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
    auto cfg = Settings().get_tricamera_driver_settings();
    float rate_sec = 1.f / cfg->frame_rate_fps;
    rate = std::chrono::milliseconds(std::lround(rate_sec * 1000));
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

}  // namespace trifinger_cameras
