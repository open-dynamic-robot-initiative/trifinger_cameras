#include <trifinger_cameras/tricamera_logger.hpp>

#include <filesystem>

#include <opencv2/core/eigen.hpp>
#include <opencv2/hdf/hdf5.hpp>

namespace trifinger_cameras
{
void TriCameraLogger::stop_and_save_hdf5(const std::string &filename)
{
    stop();

    if (buffer_.empty())
    {
        throw std::runtime_error("Buffer is empty, nothing to save.");
    }

    // existing files shall be overwritten, so if it already exists, delete the
    // old one
    std::filesystem::remove(filename);

    cv::Ptr<cv::hdf::HDF5> h5io = cv::hdf::open(filename);

    constexpr int TRICAMERA_LOG_MAGIC = 0x3CDA7A00;
    constexpr int FORMAT_VERSION_MAJOR = 2;
    constexpr int FORMAT_VERSION_MINOR = 1;
    constexpr int NUM_CAMERAS = 3;

    const std::string DS_IMAGES = "images";
    const std::string DS_CAMERA_TIMESTAMPS = "timestamps";
    const std::string DS_TIMESERIES_TIMESTAMPS = "sensor_data_timestamps";

    // check if buffer is empty
    int image_width = std::get<1>(buffer_[0]).cameras[0].image.cols;
    int image_height = std::get<1>(buffer_[0]).cameras[0].image.rows;

    h5io->atwrite(TRICAMERA_LOG_MAGIC, "magic");
    h5io->atwrite(FORMAT_VERSION_MAJOR, "format_version");
    h5io->atwrite(FORMAT_VERSION_MINOR, "format_version_minor");
    h5io->atwrite(NUM_CAMERAS, "num_cameras");
    h5io->atwrite(image_width, "image_width");
    h5io->atwrite(image_height, "image_height");

    // Add camera calibration parameters
    h5io->grcreate("/camera_info");
    TriCameraInfo info = sensor_data_->sensor_info->newest_element();

    const std::array<std::string, 3> CAMERA_NAMES = {
        "camera60", "camera180", "camera300"};
    for (size_t i = 0; i < NUM_CAMERAS; ++i)
    {
        const CameraInfo &params = info.camera[i];
        std::string group_name = "/camera_info/" + CAMERA_NAMES[i];
        h5io->grcreate(group_name);

        h5io->atwrite(params.frame_rate_fps, group_name + "/frame_rate_fps");

        // datasets are auto-created when writing, so as long as no special
        // settings like compression are needed, we can skip dscreate() here.

        cv::Mat camera_matrix;
        cv::eigen2cv(params.camera_matrix, camera_matrix);
        h5io->dswrite(camera_matrix, group_name + "/camera_matrix");

        cv::Mat distortion_coeffs;
        cv::eigen2cv(params.distortion_coefficients, distortion_coeffs);
        h5io->dswrite(distortion_coeffs,
                      group_name + "/distortion_coefficients");

        cv::Mat tf_world_to_camera;
        cv::eigen2cv(params.tf_world_to_camera, tf_world_to_camera);
        h5io->dswrite(tf_world_to_camera, group_name + "/tf_world_to_camera");
    }

    const int n_frames = static_cast<int>(buffer_.size());
    constexpr int compression_level = 4;
    std::vector<int> images_size{
        n_frames, NUM_CAMERAS, image_height, image_width};
    std::vector<int> images_chunks{1, NUM_CAMERAS, image_height, image_width};
    h5io->dscreate(
        images_size, CV_8UC1, DS_IMAGES, compression_level, images_chunks);

    // timestamps from the camera observations (when images were captured)
    h5io->dscreate(
        std::vector<int>{n_frames, NUM_CAMERAS}, CV_64F, DS_CAMERA_TIMESTAMPS);

    // timestamps from the time series (when observations were added to the
    // sensor data and thus available to the user)
    h5io->dscreate(
        std::vector<int>{n_frames}, CV_64F, DS_TIMESERIES_TIMESTAMPS);

    // Write the observations to the HDF5 file
    for (int i_obs = 0; i_obs < n_frames; ++i_obs)
    {
        // Collect the images of all cameras into one multi-dimensional mat, so
        // we can write the whole chunk at once to the HDF5 dataset (is supposed
        // to be more efficient than writing parts of the chunk separately). We
        // add a useless dimension of size 1 at the beginning, so `images`
        // already matches the dimensions of the dataset (makes it easier to
        // write to the dataset later on).
        cv::Mat images(
            std::vector<int>{1, NUM_CAMERAS, image_height, image_width},
            CV_8UC1);
        cv::Mat camera_timestamps(1, NUM_CAMERAS, CV_64F);

        double timeseries_timestamp = std::get<0>(buffer_[i_obs]);

        for (int i_cam = 0; i_cam < NUM_CAMERAS; ++i_cam)
        {
            const CameraObservation &camera =
                std::get<1>(buffer_[i_obs]).cameras[i_cam];

            // Get slice of `images` to which we can write the single image.
            // The reshape is needed to flatten out the dimensions for n_frames
            // and n_cameras (which are of size 1 in the slice).
            std::vector<cv::Range> img_range{cv::Range::all(),
                                             cv::Range(i_cam, i_cam + 1),
                                             cv::Range::all(),
                                             cv::Range::all()};
            cv::Mat images_slice = images(img_range).reshape(
                0, std::vector<int>{image_height, image_width});

            camera.image.copyTo(images_slice);

            camera_timestamps.at<double>(0, i_cam) = camera.timestamp;
        }

        h5io->dswrite(images, DS_IMAGES, std::vector<int>{i_obs, 0, 0, 0});
        h5io->dswrite(camera_timestamps,
                      DS_CAMERA_TIMESTAMPS,
                      std::vector<int>{i_obs, 0});

        // OpenCV's HDF5 interface can only write Mat to datasets, so even
        // scalar values need to be wrapped in a Mat. Use a 1-D Mat to match
        // the dataset shape.
        cv::Mat ts_mat(std::vector<int>{1}, CV_64F);
        ts_mat.at<double>(0) = timeseries_timestamp;
        h5io->dswrite(ts_mat,
                      DS_TIMESERIES_TIMESTAMPS,
                      std::vector<int>{i_obs});
    }

    h5io->close();
}
}  // namespace trifinger_cameras
