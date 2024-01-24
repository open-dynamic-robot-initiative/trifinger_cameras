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

### Removed
- Obsolete script `verify_calibration.py`

### Fixed
- pybind11 build error on Ubuntu 22.04


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
