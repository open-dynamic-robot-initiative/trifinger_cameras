/**
 * @file
 * @brief Tests for CameraObservation
 * @copyright Copyright (c) 2019, Max Planck Gesellschaft.
 */
#include <gtest/gtest.h>
#include <cereal/archives/binary.hpp>
#include <trifinger_cameras/camera_observation.hpp>

TEST(TestCameraObservation, serialization)
{
    trifinger_cameras::CameraObservation obs1, obs2;

    obs1.image = (cv::Mat_<double>(3, 3) << 1, 2, 3, 4, 5, 6, 7, 8, 9);
    obs1.timestamp = 42.0;

    std::stringstream serialized_data;  // any stream can be used

    {
        cereal::BinaryOutputArchive oarchive(serialized_data);
        oarchive(obs1);  // write data to archive
    }  // archive goes out of scope, ensuring all contents are flushed

    {
        cereal::BinaryInputArchive iarchive(serialized_data);
        iarchive(obs2);  // read data from archive
    }

    ASSERT_EQ(cv::countNonZero(obs1.image != obs2.image), 0);
    ASSERT_EQ(obs1.timestamp, obs2.timestamp);
}

int main(int argc, char **argv)
{
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
