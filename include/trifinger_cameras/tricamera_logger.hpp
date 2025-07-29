#pragma once

#include <robot_interfaces/sensors/sensor_logger.hpp>

#include <trifinger_cameras/camera_parameters.hpp>
#include <trifinger_cameras/tricamera_observation.hpp>

namespace trifinger_cameras
{
/**
 * @brief Logger for TriCamera observations with option to save to HDF5 file.
 *
 * Extends the generic robot_interfaces::SensorLogger with a method @ref
 * stop_and_save_hdf5, which saves the data to an HDF5 file instead of the
 * native binary format.
 */
class TriCameraLogger
    : public robot_interfaces::SensorLogger<TriCameraObservation, TriCameraInfo>
{
public:
    using robot_interfaces::SensorLogger<TriCameraObservation,
                                         TriCameraInfo>::SensorLogger;
    /**
     * @brief Stop logging and save logged messages to a HDF5 file.
     *
     * @param filename Path to the output file.  Existing files will be
     *     overwritten.
     */
    void stop_and_save_hdf5(const std::string &filename);
};
}  // namespace trifinger_cameras
