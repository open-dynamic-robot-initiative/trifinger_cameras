/**
 * @file
 * @brief Test serialization of cv::Mat.
 * @copyright Copyright (c) 2019, Max Planck Gesellschaft.
 */
#include <gtest/gtest.h>
#include <cereal/archives/binary.hpp>
#include <trifinger_cameras/cereal_cvmat.hpp>

TEST(TestSerializeCvMat, serialization)
{
    cv::Mat m1, m2;
    std::stringstream serialized_data;

    {
        m1 = (cv::Mat_<double>(3, 3) << 1, 2, 3, 4, 5, 6, 7, 8, 9);
        cereal::BinaryOutputArchive oarchive(serialized_data);

        oarchive(m1);
    }  // archive goes out of scope, ensuring all contents are flushed

    {
        cereal::BinaryInputArchive iarchive(serialized_data);

        iarchive(m2);
        ASSERT_EQ(cv::countNonZero(m1 != m2), 0);
    }
}

int main(int argc, char **argv)
{
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
