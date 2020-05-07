/**
 * @file
 * @brief Serialization functions for serializing `cv::Mat` with cereal.
 * @author Patrik Huber
 * @license Apache-2.0
 * @todo Move this to some "serialization tools" package
 *
 * Taken from
 * https://www.patrikhuber.ch/blog/2015/05/serialising-opencv-matrices-using-boost-and-cereal/
 */

// Copyright 2015 Patrik Huber
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// NOTE: The code was modified a bit to fix some compiler errors

#pragma once

#include <cereal/archives/binary.hpp>
#include <opencv2/opencv.hpp>

namespace cereal
{
template <class Archive>
void save(Archive& archive, const cv::Mat& mat)
{
    int rows, cols, type;
    bool continuous;

    rows = mat.rows;
    cols = mat.cols;
    type = mat.type();
    continuous = mat.isContinuous();

    archive(rows, cols, type, continuous);

    if (continuous)
    {
        const int data_size = rows * cols * static_cast<int>(mat.elemSize());
        auto mat_data = cereal::binary_data(mat.ptr(), data_size);
        archive(mat_data);
    }
    else
    {
        const int row_size = cols * static_cast<int>(mat.elemSize());
        for (int i = 0; i < rows; i++)
        {
            auto row_data = cereal::binary_data(mat.ptr(i), row_size);
            archive(row_data);
        }
    }
};

template <class Archive>
void load(Archive& archive, cv::Mat& mat)
{
    int rows, cols, type;
    bool continuous;

    archive(rows, cols, type, continuous);

    if (continuous)
    {
        mat.create(rows, cols, type);
        const int data_size = rows * cols * static_cast<int>(mat.elemSize());
        auto mat_data = cereal::binary_data(mat.ptr(), data_size);
        archive(mat_data);
    }
    else
    {
        mat.create(rows, cols, type);
        const int row_size = cols * static_cast<int>(mat.elemSize());
        for (int i = 0; i < rows; i++)
        {
            auto row_data = cereal::binary_data(mat.ptr(i), row_size);
            archive(row_data);
        }
    }
};

}  // namespace cereal
