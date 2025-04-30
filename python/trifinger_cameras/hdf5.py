"""Utilities for working with HDF5 camera log files."""

from collections.abc import Container

import h5py

from . import TRICAMERA_LOG_MAGIC


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
