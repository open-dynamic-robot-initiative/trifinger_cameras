/**
 * @file
 * @copyright 2020 Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <trifinger_cameras/settings.hpp>

#include <string_view>

namespace trifinger_cameras
{
std::shared_ptr<PylonDriverSettings> PylonDriverSettings::load_from_toml(
    const toml::table& config)
{
    auto section = config[CONFIG_SECTION];
    auto cfg = std::make_shared<PylonDriverSettings>();

    // default value of pylon_settings_file requires some lookup, so use an `if`
    // to only do that if actually needed
    std::optional<std::string> pylon_settings_file =
        section["pylon_settings_file"].value<std::string>();
    if (!pylon_settings_file)
    {
        pylon_settings_file =
            ament_index_cpp::get_package_share_directory("trifinger_cameras") +
            "/config/pylon_camera_settings.txt";
    }
    cfg->pylon_settings_file = *pylon_settings_file;

    return cfg;
}

std::ostream& operator<<(std::ostream& os, const PylonDriverSettings& s)
{
    os << "PylonDriverSettings:" << std::endl
       << "\tpylon_settings_file: " << s.pylon_settings_file << std::endl;
    return os;
}

std::shared_ptr<TriCameraDriverSettings>
TriCameraDriverSettings::load_from_toml(const toml::table& config)
{
    auto section = config[CONFIG_SECTION];
    auto cfg = std::make_shared<TriCameraDriverSettings>();

    cfg->frame_rate_fps = section["frame_rate_fps"].value_or(10.0f);

    return cfg;
}

std::ostream& operator<<(std::ostream& os, const TriCameraDriverSettings& s)
{
    os << "TriCameraDriverSettings:" << std::endl
       << "\tframe_rate_fps: " << s.frame_rate_fps << std::endl;
    return os;
}

Settings::Settings()
{
    const char* config_file_path =
        std::getenv(std::string(ENV_VARIABLE_CONFIG_FILE).c_str());
    if (config_file_path)
    {
        config_ = toml::parse_file(config_file_path);
    }
    // If no file is specified, simply do nothing here.  This results in config_
    // being an empty toml::table and thus the `load_from_toml()` functions
    // should fill all members with default values.
}

Settings::Settings(const std::filesystem::path& file)
{
    config_ = toml::parse_file(file.string());
}

std::shared_ptr<const PylonDriverSettings> Settings::get_pylon_driver_settings()
{
    if (!pylon_driver_settings_)
    {
        pylon_driver_settings_ = PylonDriverSettings::load_from_toml(config_);
    }
    return pylon_driver_settings_;
}

std::shared_ptr<const TriCameraDriverSettings>
Settings::get_tricamera_driver_settings()
{
    if (!tricamera_driver_settings_)
    {
        tricamera_driver_settings_ =
            TriCameraDriverSettings::load_from_toml(config_);
    }
    return tricamera_driver_settings_;
}

}  // namespace trifinger_cameras
