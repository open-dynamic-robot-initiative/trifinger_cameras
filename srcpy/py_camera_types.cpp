/**
 * @file
 * @brief Create bindings for camera sensors
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 * @license BSD 3-clause
 */
#include <pybind11/pybind11.h>
#include <pybind11/stl/filesystem.h>
#include <pybind11_opencv/cvbind.hpp>

#include <trifinger_cameras/camera_observation.hpp>
#include <trifinger_cameras/camera_parameters.hpp>
#include <trifinger_cameras/opencv_driver.hpp>
#include <trifinger_cameras/settings.hpp>
#ifdef Pylon_FOUND
#include <trifinger_cameras/pylon_driver.hpp>
#endif
#include <robot_interfaces/sensors/pybind_sensors.hpp>
#include <robot_interfaces/sensors/sensor_driver.hpp>

using namespace robot_interfaces;
using namespace trifinger_cameras;

PYBIND11_MODULE(py_camera_types, m)
{
    create_sensor_bindings<CameraObservation, CameraInfo>(m);

    pybind11::class_<OpenCVDriver,
                     std::shared_ptr<OpenCVDriver>,
                     SensorDriver<CameraObservation, CameraInfo>>(
        m, "OpenCVDriver")
        .def(pybind11::init<int>())
        .def("get_observation", &OpenCVDriver::get_observation);

#ifdef Pylon_FOUND
    pybind11::class_<PylonDriver,
                     std::shared_ptr<PylonDriver>,
                     SensorDriver<CameraObservation, CameraInfo>>(m,
                                                                  "PylonDriver")
        .def(pybind11::init<const std::string&, bool>(),
             pybind11::arg("device_user_id"),
             pybind11::arg("downsample_images") = true)
        .def(pybind11::init<const std::filesystem::path&, bool>(),
             pybind11::arg("camera_calibration_file"),
             pybind11::arg("downsample_images") = true)
        .def("get_sensor_info", &PylonDriver::get_sensor_info)
        .def("get_observation", &PylonDriver::get_observation);
#endif

    pybind11::class_<CameraObservation>(m, "CameraObservation")
        .def(pybind11::init<>())
        .def_readwrite("image", &CameraObservation::image, "The image.")
        .def_readwrite("timestamp",
                       &CameraObservation::timestamp,
                       "Timestamp when the image was acquired.");

    pybind11::class_<CameraInfo>(m, "CameraInfo")
        .def(pybind11::init<>())
        .def_readwrite("frame_rate_fps", &CameraInfo::frame_rate_fps)
        .def_readwrite("image_width", &CameraInfo::image_width)
        .def_readwrite("image_height", &CameraInfo::image_height)
        .def_readwrite("camera_matrix", &CameraInfo::camera_matrix)
        .def_readwrite("distortion_coefficients",
                       &CameraInfo::distortion_coefficients)
        .def_readwrite("tf_world_to_camera", &CameraInfo::tf_world_to_camera);

    pybind11::class_<PylonDriverSettings, std::shared_ptr<PylonDriverSettings>>(
        m, "PylonDriverSettings")
        .def_readonly("pylon_settings_file",
                      &PylonDriverSettings::pylon_settings_file);
    pybind11::class_<TriCameraDriverSettings,
                     std::shared_ptr<TriCameraDriverSettings>>(
        m, "TriCameraDriverSettings")
        .def_readonly("frame_rate_fps",
                      &TriCameraDriverSettings::frame_rate_fps);
    pybind11::class_<Settings>(m, "Settings")
        .def(pybind11::init<>())
        .def("get_pylon_driver_settings", &Settings::get_pylon_driver_settings)
        .def("get_tricamera_driver_settings",
             &Settings::get_tricamera_driver_settings);
}
