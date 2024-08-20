/**
 * @file
 * @brief Wrapper on the Pylon Driver to synchronise three pylon dependent
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 */
#include <trifinger_cameras/pybullet_tricamera_driver.hpp>

#include <chrono>
#include <cmath>
#include <thread>

#include <fmt/core.h>
#include <pybind11/eigen.h>
#include <pybind11/numpy.h>

#include <pybind11_opencv/cvbind.hpp>
#include <serialization_utils/cereal_cvmat.hpp>

namespace py = pybind11;

using namespace pybind11::literals;  // to bring in the `_a` litera

namespace trifinger_cameras
{
constexpr int ROBOT_STEPS_PER_SECOND = 1000;

PyBulletTriCameraDriver::PyBulletTriCameraDriver(
    robot_interfaces::TriFingerTypes::BaseDataPtr robot_data,
    bool render_images,
    Settings settings)
    : render_images_(render_images),
      robot_data_(robot_data),
      last_update_robot_time_index_(0)
{
    // compute frame rate in robot steps
    float frame_rate_fps =
        settings.get_tricamera_driver_settings()->frame_rate_fps;
    frame_rate_in_robot_steps_ =
        std::lround(ROBOT_STEPS_PER_SECOND / frame_rate_fps);

    sensor_info_.camera[0].frame_rate_fps = frame_rate_fps;
    sensor_info_.camera[1].frame_rate_fps = frame_rate_fps;
    sensor_info_.camera[2].frame_rate_fps = frame_rate_fps;

    // initialize Python interpreter if not already done
    if (!Py_IsInitialized())
    {
        py::initialize_interpreter();
    }

    py::gil_scoped_acquire acquire;

    if (render_images)
    {
        // some imports that are needed later for converting images (numpy array
        // -> cv::Mat)
        numpy_ = py::module::import("numpy");

        // TriFingerCameras gives access to the cameras in simulation
        py::module mod_camera =
            py::module::import("trifinger_simulation.camera");
        cameras_ = mod_camera.attr("TriFingerCameras")();

        // Alternatively, it is also possible to simulate actual cameras based
        // on calibration parameters:
        // py::module pathlib = py::module::import("pathlib");
        // cameras_ =
        // mod_camera.attr("create_trifinger_camera_array_from_config")(
        //   pathlib.attr("Path")("/etc/trifingerpro"),
        //   "camera{id}_cropped_and_downsampled.yml");

        // fill the sensor_info_ structure for all three cameras.
        for (size_t i = 0; i < 3; i++)
        {
            // Computations for the camera matrix and the world-to-camera
            // transformation are based on the inverse code in the
            // CalibratedCamera class in trifinger_simulation.

            py::object camera =
                static_cast<py::list>(cameras_.attr("cameras"))[i];

            int width = camera.attr("get_width")().cast<int>();
            int height = camera.attr("get_height")().cast<int>();

            sensor_info_.camera[i].image_width = width;
            sensor_info_.camera[i].image_height = height;

            // if (py::hasattr(camera, "_original_camera_matrix"))
            if (py::isinstance(camera, mod_camera.attr("CalibratedCamera")))
            {
                sensor_info_.camera[i].camera_matrix =
                    camera.attr("_original_camera_matrix")
                        .cast<Eigen::Matrix3d>();
            }
            else
            {
                // Compute focal lengths and center points from the scale and
                // shift values in the projection matrix.
                //
                // Reshape to proper 4x4 matrix so the code for element access
                // is less confusing (note that PyBullet uses Fortran order for
                // some reason).
                py::array_t<double> projection_matrix =
                    numpy_.attr("asarray")(camera.attr("_proj_matrix"))
                        .attr("reshape")(4, 4, "order"_a = "F");
                double xscale = projection_matrix.at(0, 0);
                double yscale = projection_matrix.at(1, 1);
                double xshift = projection_matrix.at(0, 2);
                double yshift = projection_matrix.at(1, 2);
                double cx = -(width * (xshift - 1)) / 2;
                double cy = (height * (yshift + 1)) / 2;
                double fx = xscale * width / 2;
                double fy = yscale * height / 2;
                sensor_info_.camera[i].camera_matrix << fx, 0, cx, 0, fy, cy, 0,
                    0, 1;
            }

            // The view matrix is flattened in Fortran order, so reshape
            // accordingly to get the proper 4x4 matrix.
            Eigen::Matrix4d view_matrix =
                numpy_.attr("asarray")(camera.attr("_view_matrix"))
                    .attr("reshape")(4, 4, "order"_a = "F")
                    .cast<Eigen::Matrix4d>();

            // To get the proper world-to-camera transformation, the view matrix
            // needs to be rotated by 180° around the x-axis.
            Eigen::Matrix4d rot_x_180;
            rot_x_180 << 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1;
            sensor_info_.camera[i].tf_world_to_camera = rot_x_180 * view_matrix;
        }
    }
}

TriCameraInfo PyBulletTriCameraDriver::get_sensor_info()
{
    return sensor_info_;
}

TriCameraObservation PyBulletTriCameraDriver::get_observation()
{
    time_series::Index robot_t =
        robot_data_->observation->newest_timeindex(false);
    if (robot_t == time_series::EMPTY)
    {
        // As long as robot backend did not start yet, run at around 10 Hz
        using namespace std::chrono_literals;
        std::this_thread::sleep_for(100ms);
    }
    else
    {
        // Synchronize with robot backend:  To achieve the desired frame rate,
        // there should be one camera observation every
        // `frame_rate_in_robot_steps_` robot steps.
        while (robot_t <
               last_update_robot_time_index_ + frame_rate_in_robot_steps_)
        {
            using namespace std::chrono_literals;
            // TODO the sleep here might be problematic if very high frame rate
            // is required
            std::this_thread::sleep_for(10ms);
            auto new_robot_t =
                robot_data_->observation->newest_timeindex(false);

            // If robot t did not increase, assume the robot has stopped.
            // Break this loop to avoid a dead-lock.
            if (new_robot_t == robot_t)
            {
                break;
            }
            robot_t = new_robot_t;
        }
        last_update_robot_time_index_ = robot_t;
    }

    trifinger_cameras::TriCameraObservation observation;

    auto current_time = std::chrono::system_clock::now();
    double timestamp =
        std::chrono::duration<double>(current_time.time_since_epoch()).count();
    for (int i = 0; i < 3; i++)
    {
        observation.cameras[i].timestamp = timestamp;
    }

    {
        py::gil_scoped_acquire acquire;

        // skip the rendering if render_images_ == false.  In this case the
        // images in the observation will simply be uninitialised.
        if (render_images_)
        {
            py::list images = cameras_.attr("get_bayer_images")();
            for (int i = 0; i < 3; i++)
            {
                // ensure that the image array is contiguous in memory,
                // otherwise conversion to cv::Mat would fail
                auto image = numpy_.attr("ascontiguousarray")(images[i]);
                cv::Mat image_cv = image.cast<cv::Mat>();
                // explicitly copy to ensure it is not pointing to some data
                // that later gets invalid
                image_cv.copyTo(observation.cameras[i].image);
            }
        }
    }

    return observation;
}

}  // namespace trifinger_cameras
