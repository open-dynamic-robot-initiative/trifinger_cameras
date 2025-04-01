# Changelog

## [Unreleased]
### Added
- Script `overlay_real_and_rendered_images.py` for verifying camera calibration.
- Utility function `check_image_sharpness()` to evaluate how sharp an image is and a
  script `check_camera_sharpness` to easily test different parameters on live camera
  data.  This can be used, for example, to automatically detect if a camera is
  significantly out of focus.
- Executable `pylon_write_device_user_id_to_camera` to set the "DeviceUserID" of
  Pylon cameras.
- Executable `pylon_dump_camera_settings` to save settings of a Pylon camera.
- Make some settings (e.g. frame rate) configurable through a TOML config file.  For
  more information see
  [documentation](https://open-dynamic-robot-initiative.github.io/trifinger_cameras/doc/configuration.html)
- Executable `tricamera_monitor_rate` for checking the actual frame rate (most meant for
  debugging and testing during development)
- Executables `single_camera_backend` and `tricamera_backend` to run camera back ends in
  a separate process (mostly for testing).  Also added `--multi-process` option to
  `demo_camera.py` accordingly.
- Implement `get_sensor_info()` for Pylon and PyBullet drivers.  See `demo_camera` and
  `demo_tricamera` on how to use it.
- Executable `record_tricamera_log` for recording camera data for testing, etc.
- Executable `tricamera_log_extract` for extracting still images from a camera log file.

### Removed
- Obsolete script `verify_calibration.py`

### Fixed
- pybind11 build error on Ubuntu 22.04
- Connecting to camera without specifying DeviceUserID was not working.  It now opens
  the first camera in the list of connected cameras if no ID is specified.
- Export dependencies needed when using the `pylon_driver` library in an other package.

### Changed
- `pylon_list_cameras`:  Keep stdout clean if there are no cameras.
- Camera calibration YAML files are now compatible with OpenCVs YAML parser.


## [1.0.0] - 2022-06-28
### Added
- Executable `pylon_list_cameras` which lists all detected Pylon cameras.

### Removed
- Old calibration images that were stored in this package.


## [0.2.0] - 2021-08-04

There is no changelog for this or earlier versions.


[Unreleased]: https://github.com/open-dynamic-robot-initiative/trifinger_cameras/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/open-dynamic-robot-initiative/trifinger_cameras/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/open-dynamic-robot-initiative/trifinger_cameras/releases/tag/v0.2.0
