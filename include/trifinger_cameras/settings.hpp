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
#include <toml++/toml.hpp>

namespace trifinger_cameras
{
//! Settings of the PylonDriver.
struct PylonDriverSettings
{
    //! Name of the corresponding section in the config file
    static constexpr std::string_view CONFIG_SECTION = "pylon_driver";

    /**
     * @brief Path to the file with the settings that are sent to the Pylon
     * camera.
     */
    std::string pylon_settings_file;

    //! Load from TOML table, using default values for unspecified parameters.
    static std::shared_ptr<PylonDriverSettings> load_from_toml(
        const toml::table& config);
};

//! Settings of the TriCameraDriver.
struct TriCameraDriverSettings
{
    //! Name of the corresponding section in the config file
    static constexpr std::string_view CONFIG_SECTION = "tricamera_driver";

    /**
     * @brief Frame rate at which images are fetched from the camera.
     *
     * Important: This must not be higher than ``AcquisitionFrameRate`` which is
     * defined in the Pylon settings file.
     */
    float frame_rate_fps;

    //! Load from TOML table, using default values for unspecified parameters.
    static std::shared_ptr<TriCameraDriverSettings> load_from_toml(
        const toml::table& config);
};

/**
 * @brief Central class for loading settings.
 *
 * @verbatim embed:rst:leading-asterisk
 *
 * Central facility to load settings for this package from a TOML file.
 *
 * For information about the config file format, see :ref:`configuration`.
 *
 * Constructing the class will parse the TOML file but actual settings objects
 * for the different modules are only created when the corresponding getter is
 * called the first time.
 *
 * @endverbatim
 */
class Settings
{
public:
    //! Name of the environment variable to specify the config file path.
    static constexpr std::string_view ENV_VARIABLE_CONFIG_FILE =
        "TRIFINGER_CAMERA_CONFIG";

    /**
     * @brief Load configuration from file specified via environment variable.
     *
     * If the environment variable ``TRIFINGER_CAMERA_CONFIG`` is defined, it is
     * expected to contain the path to the configuration file, which is then
     * loaded.  If it is not defined, default values are used for all
     * parameters.
     */
    Settings();

    //! Load configuration from the specified file.
    Settings(const std::filesystem::path& file);

    //! Get settings for the PylonDriver.
    std::shared_ptr<const PylonDriverSettings> get_pylon_driver_settings();

    //! Get settings for the TriCameraDriver.
    std::shared_ptr<const TriCameraDriverSettings>
    get_tricamera_driver_settings();

private:
    toml::table config_;
    std::shared_ptr<PylonDriverSettings> pylon_driver_settings_;
    std::shared_ptr<TriCameraDriverSettings> tricamera_driver_settings_;

    void parse_file(const std::filesystem::path& file);
};

}  // namespace trifinger_cameras
