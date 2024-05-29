.. _configuration:

*************
Configuration
*************

Some parameters of the Pylon driver classes can be configured via a TOML configuration
file.

Configuration Options
=====================

The configuration file has to be in TOML format.  Below is an overview of the supported
sections/settings and their default values.  All settings are optional.  If not
specified the default values are used.

.. code-block:: toml

    [pylon_driver]
    pylon_settings_file = "path/to/default_pylon_camera_settings.txt"

    [tricamera_driver]
    frame_rate_fps = 10.0


pylon_driver
------------

Settings concerning all Pylon cameras.

.. list-table::

   * - ``pylon_settings_file``
     - Path to the file containing the settings for the Pylon SDK (see
       :ref:`pylon_settings_file`).  If not set, the default settings file shipped with
       this package is used (see :ref:`default_pylon_camera_settings`).


tricamera_driver
----------------

Settings specific to :cpp:class:`~trifinger_cameras::TriCameraDriver`.

.. list-table::

   * - ``frame_rate_fps``
     - Frequency at which frames are fetched from the cameras.  **Important:** This is
       limited by the ``AcquisitionFrameRate`` setting in the
       :ref:`pylon_settings_file`, i.e. make sure to set ``AcquisitionFrameRate >=
       frame_rate_fps``.


How to use the custom configuration
===================================

To use the file, simply write the path to the environment variable
``TRIFINGER_CAMERA_CONFIG``.

Alternatively, if you instantiate the :cpp:class:`~trifinger_cameras::PylonDriver` or
:cpp:class:`~trifinger_cameras::TriCameraDriver` classes in your own code, you can create a
:cpp:class:`~trifinger_cameras::Settings` instance (specify the path to the TOML file in the constructor)
and pass this to the constructor of the driver class.


.. _pylon_settings_file:

Pylon Settings
==============

The driver for Pylon cameras uses the Pylon SDK, which allows configuration of camera
settings like frame rate, white balancing, etc.
These settings are stored in a file, which is loaded by the
:cpp:class:`~trifinger_cameras::PylonDriver` class during initialisation.  The path to
this file can be configured through the ``pylon_settings_file`` setting (see above).

This package ships with a default settings file (see
:ref:`default_pylon_camera_settings`).  For simple changes like adjusting the frame
rate, you may simply copy that file and change the corresponding values.
For more complex changes, it is recommended to use the graphical interface of the
Pylon Viewer application (part of the SDK) and then save the settings to a file using
TODO.

.. todo:: instructions on how to save settings to file
