/**
 * @file
 * @brief Tests for Settings etc.
 * @copyright Copyright (c) 2019, Max Planck Gesellschaft.
 */
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string_view>
#include <trifinger_cameras/settings.hpp>

using namespace trifinger_cameras;
using ::testing::NotNull;

// `ends_with` taken from https://stackoverflow.com/a/42844629 by Pavel P (CC
// BY-SA 4.0)
static bool ends_with(std::string_view str, std::string_view suffix)
{
    return str.size() >= suffix.size() &&
           str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
}

TEST(TestSettings, load_env_no_file)
{
    // make sure the env variable is _not_ set
    unsetenv(std::string(Settings::ENV_VARIABLE_CONFIG_FILE).c_str());
    Settings s;

    auto pylon_driver_settings = s.get_pylon_driver_settings();
    auto tricamera_driver_settings = s.get_tricamera_driver_settings();
    ASSERT_THAT(pylon_driver_settings, NotNull());
    ASSERT_THAT(tricamera_driver_settings, NotNull());
    EXPECT_TRUE(ends_with(pylon_driver_settings->pylon_settings_file,
                          "config/pylon_camera_settings.txt"));
    EXPECT_FLOAT_EQ(tricamera_driver_settings->frame_rate_fps, 10.);
}

TEST(TestSettings, load_env_file_with_full_config)
{
    std::string tmpfile = std::tmpnam(nullptr);
    std::ofstream out(tmpfile);
    out << R"TOML(
[pylon_driver]
pylon_settings_file = "path/to/file.txt"

[tricamera_driver]
frame_rate_fps = 42.1

[unrelated_section]
should_not_harm = true
)TOML";
    out.close();

    setenv(std::string(Settings::ENV_VARIABLE_CONFIG_FILE).c_str(),
           tmpfile.c_str(),
           true);
    Settings s;

    auto pylon_driver_settings = s.get_pylon_driver_settings();
    auto tricamera_driver_settings = s.get_tricamera_driver_settings();
    ASSERT_THAT(pylon_driver_settings, NotNull());
    ASSERT_THAT(tricamera_driver_settings, NotNull());
    EXPECT_EQ(pylon_driver_settings->pylon_settings_file, "path/to/file.txt");
    EXPECT_FLOAT_EQ(tricamera_driver_settings->frame_rate_fps, 42.1);

    std::remove(tmpfile.c_str());
}

TEST(TestSettings, load_file_without_config)
{
    std::string tmpfile = std::tmpnam(nullptr);
    std::ofstream out(tmpfile);
    out << "# no config here";
    out.close();

    Settings s(tmpfile);

    auto pylon_driver_settings = s.get_pylon_driver_settings();
    auto tricamera_driver_settings = s.get_tricamera_driver_settings();
    ASSERT_THAT(pylon_driver_settings, NotNull());
    ASSERT_THAT(tricamera_driver_settings, NotNull());
    EXPECT_TRUE(ends_with(pylon_driver_settings->pylon_settings_file,
                          "config/pylon_camera_settings.txt"));
    EXPECT_FLOAT_EQ(tricamera_driver_settings->frame_rate_fps, 10.0);

    std::remove(tmpfile.c_str());
}

TEST(TestSettings, load_file_with_full_config)
{
    std::string tmpfile = std::tmpnam(nullptr);
    std::ofstream out(tmpfile);
    out << R"TOML(
[pylon_driver]
pylon_settings_file = "path/to/file.txt"

[tricamera_driver]
frame_rate_fps = 42.1

[unrelated_section]
should_not_harm = true
)TOML";
    out.close();

    Settings s(tmpfile);

    auto pylon_driver_settings = s.get_pylon_driver_settings();
    auto tricamera_driver_settings = s.get_tricamera_driver_settings();
    ASSERT_THAT(pylon_driver_settings, NotNull());
    ASSERT_THAT(tricamera_driver_settings, NotNull());
    EXPECT_EQ(pylon_driver_settings->pylon_settings_file, "path/to/file.txt");
    EXPECT_FLOAT_EQ(tricamera_driver_settings->frame_rate_fps, 42.1);

    std::remove(tmpfile.c_str());
}

TEST(TestSettings, load_file_with_partial_config)
{
    std::string tmpfile = std::tmpnam(nullptr);
    std::ofstream out(tmpfile);
    out << R"TOML(
[pylon_driver]
pylon_settings_file = "path/to/file.txt"

[tricamera_driver]
# section exists but no value
)TOML";
    out.close();

    Settings s(tmpfile);

    auto pylon_driver_settings = s.get_pylon_driver_settings();
    auto tricamera_driver_settings = s.get_tricamera_driver_settings();
    ASSERT_THAT(pylon_driver_settings, NotNull());
    ASSERT_THAT(tricamera_driver_settings, NotNull());
    EXPECT_EQ(pylon_driver_settings->pylon_settings_file, "path/to/file.txt");
    EXPECT_FLOAT_EQ(tricamera_driver_settings->frame_rate_fps, 10.0);

    std::remove(tmpfile.c_str());
}

int main(int argc, char **argv)
{
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
