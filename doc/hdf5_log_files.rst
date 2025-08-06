***************************
TriCameraLogger HDF5 Format
***************************

The :cpp:class:`~trifinger_cameras::TriCameraLogger` provides a method
:cpp:func:`~trifinger_cameras::TriCameraLogger::stop_and_save_hdf5`, which stores the
logged data to an HDF5 file.

Further, the script :ref:`executable_tricamera_log_to_hdf5` can be used to convert
existing TriCamera logs from the legacy binary dump file (produced by :cpp:func:`robot_interfaces::SensorLogger::stop_and_save`) to HDF5.


Root Attributes
===============

- ``magic``: Magic byte to easily identify the file as a TriCamera log.
- ``format_version``: Major version of the file format (used for compatibility checks)
- ``format_version_minor``: Minor version of the file format (used for compatibility checks)
- ``num_cameras``: Number of cameras (should always be 3).
- ``image_width``: Width of the recorded images.
- ``image_height``: Height of the recorded images.


Camera Parameters
=================

There are three groups ``/camera_info/camera60``, ``/camera_info/camera180`` and
``/camera_info/camera300`` which contain the intrinsic and extrinsic parameters of the
corresponding parameters.

Each of these groups contains:

- Attribute ``frame_rate_fps`` with the frame rate of the camera (should be the same for
  all cameras but is recorded separately for consistency).
- Datasets ``camera_matrix`` (3x3), ``distortion_coefficients`` (1x5) with intrinsic parameters.
- Dataset ``tf_world_to_camera`` (4x4) with homogeneous transformation matrix from world
  to camera frame.

This corresponds to the data contained in
:cpp:struct:``~trifinger_cameras::CameraInfo``.


Camera Observations
===================

- Dataset ``/images``:  The actual images.  Dimensions are ``(n_observations, n_cameras,
  image_height, image_width)``.  Individual images are single-channel and need to be
  demosaiced before usage.
- Dataset ``/timestamps``: Timestamps of the images, when they where acquired from the
  cameras.  For each there are separate timestamps for the different cameras as they may
  not be perfectly synchronised.  Corresponds to the timestamps included in :cpp:class:`~trifinger_cameras::TriCameraObservation`.  Shape ``(n_observations, n_cameras)``.
- Dataset ``/sensor_data_timestamps``:  Timestamps of when the observation was added to
  the sensor data (that is, when it was available to the user).  Corresponds to the
  timestamp provided by :cpp:func:`robot_interfaces::SensorFrontend::get_timestamp_ms`.
  Might be useful to replay the data with the same timing as it had when recording.

