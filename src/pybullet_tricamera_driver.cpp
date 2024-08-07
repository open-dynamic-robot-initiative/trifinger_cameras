/**
 * @file
 * @brief Wrapper on the Pylon Driver to synchronise three pylon dependent
 * cameras.
 * @copyright 2020, Max Planck Gesellschaft. All rights reserved.
 */
#include <trifinger_cameras/pybullet_tricamera_driver.hpp>

#include <chrono>
#include <thread>

#include <pybind11_opencv/cvbind.hpp>
#include <serialization_utils/cereal_cvmat.hpp>

namespace py = pybind11;

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
    }
}

trifinger_cameras::TriCameraObservation
PyBulletTriCameraDriver::get_observation()
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
