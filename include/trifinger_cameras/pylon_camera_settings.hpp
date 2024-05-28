/**
 * @file
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#pragma once

#include <filesystem>
#include <ostream>
#include <string>

#include <ament_index_cpp/get_package_share_directory.hpp>

namespace trifinger_cameras
{
//! Get path to default Pylon settings file.
std::string get_default_pylon_settings_file();

/**
 * @brief Bundles all configurable camera settings.
 */
struct PylonCameraSettings
{
    /**
     * @brief Frame rate at which images are fetched from the camera.
     *
     * Important: This must not be higher than ``AcquisitionFrameRate`` which is
     * defined in the Pylon settings file.
     */
    float frame_rate_fps;

    /**
     * @brief Path to the file with the settings that are sent to the Pylon
     * camera.
     */
    std::string pylon_settings_file;

    /**
     * @brief Get default settings.
     */
    static PylonCameraSettings defaults();

    /**
     * @brief Load settings
     *
     * If the environment variable ``TRICAMERA_CONFIG_FILE`` is defined, try
     * loading settings from the file it points to (using @ref load(const
     * std::filesystem::path&)), otherwise return default settings..
     */
    static PylonCameraSettings load();

    /**
     * @brief Load settings from TOML file.
     *
     * For fields that are not specified in the provided file, the default
     * values as provided by @ref CameraSettings::defaults() are used.
     *
     * @param file Path to TOML file.
     */
    static PylonCameraSettings load(const std::filesystem::path& file);
};

std::ostream& operator<<(std::ostream& os, const PylonCameraSettings& cp);

}  // namespace trifinger_cameras
