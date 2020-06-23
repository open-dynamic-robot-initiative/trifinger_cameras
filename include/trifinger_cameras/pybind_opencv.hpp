/**
 * @file
 * @brief pybind11 binding for cv::Mat.
 */
#pragma once

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

namespace trifinger_cameras
{
void pybind_cvmat(pybind11::module& m)
{
    // NOTE: this currently only supports types 8UC1 and 8UC3 but should be
    // easy to extend to other types if needed.
    pybind11::class_<cv::Mat>(m, "cvMat", pybind11::buffer_protocol())
        .def("__init__",
             [](cv::Mat& mat, pybind11::buffer buffer) {
                 // based on
                 // https://pybind11.readthedocs.io/en/stable/advanced/pycpp/numpy.html?highlight=buffer#buffer-protocol

                 // Request a buffer descriptor from Python
                 pybind11::buffer_info info = buffer.request();

                 // Some sanity checks ...
                 if (info.format !=
                     pybind11::format_descriptor<uint8_t>::format())
                     throw std::runtime_error(
                         "Incompatible format: expected a double array!");

                 if (info.ndim != 3)
                     throw std::runtime_error("Incompatible buffer dimension!");

                 int type;
                 switch (info.shape[2])
                 {
                     case 1:
                         type = CV_8UC1;
                         break;
                     case 3:
                         type = CV_8UC3;
                         break;
                     default:
                         throw std::runtime_error(
                             "Incompatible number of channels.");
                 }

                 // create a temporary cv::Mat with the buffer data
                 cv::Mat foo(info.shape[0], info.shape[1], type, info.ptr);
                 // initialize the output matrix to the proper size/type.
                 {
                     // the following is pure C++, so the GIL can be released
                     pybind11::gil_scoped_release release_gil;

                     new (&mat) cv::Mat(foo.rows, foo.cols, foo.type());
                     // copy data from the temp. matrix to the output one (foo
                     // is only pointing to the data of buffer).
                     foo.copyTo(mat);
                 }
             })
        .def_buffer([](cv::Mat& im) -> pybind11::buffer_info {
            // based on
            // https://alexsm.com/pybind11-buffer-protocol-opencv-to-numpy/
            return pybind11::buffer_info(
                // Pointer to buffer
                im.data,
                // Size of one scalar
                sizeof(uint8_t),
                // Python struct-style format descriptor
                pybind11::format_descriptor<uint8_t>::format(),
                // Number of dimensions
                3,
                // Buffer dimensions
                {im.rows, im.cols, im.channels()},
                // Strides (in bytes) for each index
                {sizeof(uint8_t) * im.channels() * im.cols,
                 sizeof(uint8_t) * im.channels(),
                 sizeof(uint8_t)});
        });
}
}  // namespace trifinger_cameras
