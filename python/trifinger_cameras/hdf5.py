"""Utilities for working with HDF5 camera log files."""

from collections.abc import Container
from typing import Iterable, Sequence

import h5py
import numpy as np

from . import CAMERA_NAMES, TRICAMERA_LOG_MAGIC
from .camera_calibration_file import CameraCalibrationFile
from .py_tricamera_types import TriCameraObservation


def verify_tricamera_hdf5(h5file: h5py.File, supported_formats: Container[int]) -> None:
    """Verify that the HDF5 file is a valid TriCamera log file of a supported version.

    Args:
        h5file: Opened HDF5 file.
        supported_formats: Supported file formats.

    Raises:
        ValueError: If the file is not a valid TriCamera log file (based on magic byte)
            or the format version is not supported.
    """
    if h5file.attrs.get("magic") != TRICAMERA_LOG_MAGIC:
        msg = "Input file doesn't seem to be a TriCamera log file (bad magic byte)."
        raise ValueError(msg)

    if h5file.attrs["format_version"] not in supported_formats:
        msg = f"Unsupported file format version {h5file.attrs['format_version']}"
        raise ValueError(msg)


def init_tricamera_hdf5(
    h5: h5py.File, camera_params: Sequence[CameraCalibrationFile], n_frames: int
) -> None:
    """Create attributes and datasets in the given HDF5 file."""
    if len(camera_params) != len(CAMERA_NAMES):
        msg = "Length of `camera_params` doesn't match expected number of cameras"
        raise ValueError(msg)

    img_width = camera_params[0]["image_width"]
    img_height = camera_params[0]["image_height"]

    h5.create_dataset("camera_names", data=[name.encode() for name in CAMERA_NAMES])
    h5.attrs["magic"] = TRICAMERA_LOG_MAGIC
    h5.attrs["format_version"] = 2
    h5.attrs["format_version_minor"] = 1
    h5.attrs["num_cameras"] = len(CAMERA_NAMES)
    h5.attrs["image_width"] = img_width
    h5.attrs["image_height"] = img_height

    # Add camera calibration parameters
    calib_group = h5.create_group("camera_info")
    for i, params in enumerate(camera_params):
        cam_group = calib_group.create_group(CAMERA_NAMES[i])
        cam_group.create_dataset(
            "camera_matrix", data=params.get_array("camera_matrix")
        )
        cam_group.create_dataset(
            "distortion_coefficients",
            data=params.get_array("distortion_coefficients"),
        )
        cam_group.create_dataset(
            "tf_world_to_camera", data=params.get_array("tf_world_to_camera")
        )

    h5.create_dataset(
        "images",
        shape=(n_frames, len(CAMERA_NAMES), img_height, img_width),
        dtype=np.uint8,
        chunks=(1, len(CAMERA_NAMES), img_height, img_width),
        compression="gzip",
        shuffle=True,
    )

    # timestamps from the camera observations
    h5.create_dataset(
        "timestamps",
        shape=(n_frames, len(CAMERA_NAMES)),
        dtype=np.double,
    )

    # timestamps from the sensor data time series
    h5.create_dataset(
        "sensor_data_timestamps",
        shape=(n_frames,),
        dtype=np.double,
    )


def write_tricamera_hdf5(
    h5: h5py.File,
    camera_params: Sequence[CameraCalibrationFile],
    n_frames: int,
    stamped_observations: Iterable[tuple[TriCameraObservation, int]],
) -> None:
    init_tricamera_hdf5(h5, camera_params, n_frames)

    for i_obs, (observation, data_timestamp) in enumerate(stamped_observations):
        cameras = observation.cameras
        h5["images"][i_obs] = [camera.image for camera in cameras]
        h5["timestamps"][i_obs] = [camera.timestamp for camera in cameras]
        h5["sensor_data_timestamps"][i_obs] = data_timestamp
