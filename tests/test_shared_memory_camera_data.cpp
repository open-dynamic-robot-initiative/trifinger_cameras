/**
 * @file
 * @brief Tests for CameraObservation
 * @copyright Copyright (c) 2019, Max Planck Gesellschaft.
 */
#include <gtest/gtest.h>
#include <robot_interfaces/sensors/sensor_data.hpp>
#include <trifinger_cameras/camera_observation.hpp>

TEST(TestSharedMemoryCameraData, serialization)
{
    using CameraObservation = trifinger_cameras::CameraObservation;

    robot_interfaces::MultiProcessSensorData<CameraObservation> data(
        "test_camera_data", true);
    CameraObservation obs1, obs2;

    obs1.image = (cv::Mat_<double>(3, 3) << 1, 2, 3, 4, 5, 6, 7, 8, 9);
    obs1.time_stamp = 42.0;

    data.observation->append(obs1);
    obs2 = data.observation->newest_element();

    ASSERT_EQ(cv::countNonZero(obs1.image != obs2.image), 0);
    ASSERT_EQ(obs1.time_stamp, obs2.time_stamp);
}

int main(int argc, char **argv)
{
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
