/**
 * @file
 * @brief Create bindings for three pylon dependent camera sensors
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <pybind11/stl/filesystem.h>

#include <trifinger_cameras/pybullet_tricamera_driver.hpp>
#include <trifinger_cameras/tricamera_observation.hpp>
#ifdef Pylon_FOUND
#include <trifinger_cameras/tricamera_driver.hpp>
#endif

#include <robot_interfaces/sensors/pybind_sensors.hpp>
#include <robot_interfaces/sensors/sensor_driver.hpp>

using namespace robot_interfaces;
using namespace trifinger_cameras;

PYBIND11_MODULE(py_tricamera_types, m)
{
    create_sensor_bindings<TriCameraObservation, TriCameraInfo>(m);

#ifdef Pylon_FOUND
    pybind11::class_<TriCameraDriver,
                     std::shared_ptr<TriCameraDriver>,
                     SensorDriver<TriCameraObservation, TriCameraInfo>>(
        m, "TriCameraDriver")
        .def(pybind11::init<const std::string&,
                            const std::string&,
                            const std::string&,
                            bool>(),
             pybind11::arg("camera1"),
             pybind11::arg("camera2"),
             pybind11::arg("camera3"),
             pybind11::arg("downsample_images") = true)
        .def(pybind11::init<const std::filesystem::path&,
                            const std::filesystem::path&,
                            const std::filesystem::path&,
                            bool>(),
             pybind11::arg("camera_calibration_file_1"),
             pybind11::arg("camera_calibration_file_2"),
             pybind11::arg("camera_calibration_file_3"),
             pybind11::arg("downsample_images") = true)
        .def_readonly("rate", &TriCameraDriver::rate)
        .def("get_sensor_info", &TriCameraDriver::get_sensor_info)
        .def("get_observation", &TriCameraDriver::get_observation);
#endif

    pybind11::class_<TriCameraInfo>(m, "TriCameraInfo")
        .def(pybind11::init<>())
        .def_readwrite("camera", &TriCameraInfo::camera);

    pybind11::class_<TriCameraObservation>(
        m, "TriCameraObservation", "Observation from the three cameras.")
        .def(pybind11::init<>())
        .def_readwrite(
            "cameras",
            &TriCameraObservation::cameras,
            "List[~trifinger_cameras.camera.CameraObservation]: List of "
            "observations from cameras 'camera60', 'camera180' and 'camera300' "
            "(in this order)");

    pybind11::class_<PyBulletTriCameraDriver,
                     std::shared_ptr<PyBulletTriCameraDriver>,
                     SensorDriver<TriCameraObservation, TriCameraInfo>>(
        m, "PyBulletTriCameraDriver")
        .def(pybind11::init<robot_interfaces::TriFingerTypes::BaseDataPtr,
                            bool>(),
             pybind11::arg("robot_data"),
             pybind11::arg("render_images") = true)
        .def("get_sensor_info", &PyBulletTriCameraDriver::get_sensor_info)
        .def("get_observation", &PyBulletTriCameraDriver::get_observation);
}
