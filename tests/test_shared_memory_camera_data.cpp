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
        "test_camera_data", true, 10);
    CameraObservation obs1, obs2;

    obs1.image = cv::Mat::ones(
        CameraObservation::height, CameraObservation::width, CV_8UC1);
    // change a few bytes, so that its not just all ones
    obs1.image.data[0] = 13;
    obs1.image.data[4] = 42;
    obs1.image.data[13] = 123;
    obs1.timestamp = 42.0;

    data.observation->append(obs1);
    obs2 = data.observation->newest_element();

    ASSERT_EQ(cv::countNonZero(obs1.image != obs2.image), 0);
    ASSERT_EQ(obs1.timestamp, obs2.timestamp);
}

int main(int argc, char **argv)
{
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
