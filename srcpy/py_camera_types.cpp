/**
 * @file
 * @brief Create bindings for camera sensors
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */

#include <trifinger_cameras/camera_observation.hpp>
#include <trifinger_cameras/opencv_driver.hpp>
#include <trifinger_cameras/pybind_opencv.hpp>
#ifdef Pylon_FOUND
#include <trifinger_cameras/pylon_driver.hpp>
#endif
#include <robot_interfaces/sensors/pybind_sensors.hpp>
#include <robot_interfaces/sensors/sensor_driver.hpp>

using namespace robot_interfaces;
using namespace trifinger_cameras;

PYBIND11_MODULE(py_camera_types, m)
{
    create_sensor_bindings<CameraObservation>(m);
    pybind_cvmat(m);

    pybind11::class_<OpenCVDriver,
                     std::shared_ptr<OpenCVDriver>,
                     SensorDriver<CameraObservation>>(m, "OpenCVDriver")
        .def(pybind11::init<int>())
        .def("get_observation", &OpenCVDriver::get_observation);

#ifdef Pylon_FOUND
    pybind11::class_<PylonDriver,
                     std::shared_ptr<PylonDriver>,
                     SensorDriver<CameraObservation>>(m, "PylonDriver")
        .def(pybind11::init<const std::string&, bool>(),
             pybind11::arg("device_user_id"),
             pybind11::arg("downsample_images") = true)
        .def("get_observation", &PylonDriver::get_observation);
#endif

    pybind11::class_<CameraObservation>(m, "CameraObservation")
        .def(pybind11::init<>())
        .def_readwrite("image", &CameraObservation::image)
        .def_readwrite("timestamp", &CameraObservation::timestamp);
}
