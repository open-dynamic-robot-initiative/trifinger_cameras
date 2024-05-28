/**
 * @file
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/pylon_camera_settings.hpp>

#include <string_view>

#include <toml++/toml.hpp>

namespace trifinger_cameras
{
constexpr std::string_view ENV_VARIABLE_CONFIG_FILE = "TRICAMERA_CONFIG_FILE";
constexpr std::string_view TOML_SECTION = "tricamera";

std::string get_default_pylon_settings_file()
{
    return ament_index_cpp::get_package_share_directory("trifinger_cameras") +
           "/config/pylon_camera_settings.txt";
}

PylonCameraSettings defaults()
{
    return {.frame_rate_fps = 10,
            .pylon_settings_file = get_default_pylon_settings_file()};
}

PylonCameraSettings load()
{
    const char* config_file_path =
        std::getenv(std::string(ENV_VARIABLE_CONFIG_FILE).c_str());
    if (config_file_path)
    {
        return PylonCameraSettings::load(config_file_path);
    }
    else
    {
        return PylonCameraSettings::defaults();
    }
}

PylonCameraSettings load(const std::filesystem::path& file)
{
    PylonCameraSettings defaults = PylonCameraSettings::defaults();

    auto toml_settings = toml::parse_file(file.string());

    float fps =
        toml_settings[TOML_SECTION]["fps"].value_or(defaults.frame_rate_fps);
    std::string_view pylon_settings_file =
        toml_settings[TOML_SECTION]["pylon_settings_file"].value_or(
            defaults.pylon_settings_file);

    return {.frame_rate_fps = fps,
            .pylon_settings_file = std::string{pylon_settings_file}};
}

std::ostream& operator<<(std::ostream& os, const PylonCameraSettings& cs)
{
    os << "CameraSettings:" << std::endl
       << "\tfps: " << cs.frame_rate_fps << std::endl
       << "\tpylon_settings_file: " << cs.pylon_settings_file << std::endl;
    return os;
}
}  // namespace trifinger_cameras
