***********
Executables
***********

The package contains a number of executables for calibration, testing, data
analysis, etc.

They can all be run like this:

::

    ros2 run trifinger_cameras <executable-name> [<arguments>]

For example

::

    ros2 run trifinger_cameras tricamera_log_viewer path/to/camera_data.dat 


.. todo::

   The following executables are not yet documented.  In many cases you can get
   some information by running them with ``--help``, though.

   - analyze_tricamera_log
   - calibrate_cameras
   - calibrate_trifingerpro_cameras
   - camera_log_viewer
   - charuco_board
   - check_camera_sharpness
   - convert_to_camera_pose
   - detect_aruco_marker
   - load_camera_config_test
   - overlay_camera_stream
   - overlay_real_and_rendered_images
   - pylon_list_cameras
   - record_image_dataset
   - tricamera_log_converter
   - tricamera_log_viewer
   - tricamera_test_connection



Demo Applications
=================

There are two demo applications to illustrate how to access the camera images
in your code:

- ``demo_camera.py`` for a single camera.  This works with both a Pylon camera
  or (set the ``--pylon`` flag in this case) or a regular webcam.
- ``demo_tricamera.py`` for a set of three Pylon cameras (like in the TriFinger
  platforms).

Apart from showing how to use the software, they can also be useful as simple
viewer applications for basic tests.

Run with ``--help`` to get a full list of options for each demo.



check_camera_sharpness
======================

Show live image of a Pylon camera and indicate whether it passes the sharpness
test.

.. image:: images/screenshot_check_camera_sharpness_gui.jpg

The sharpness of the image is evaluated by running Canny edge detection on the
image and computing the mean value of the resulting edge image.  A higher value
means more edges which indicates a sharper image.

The result of the edge detection is shown in the GUI next to the camera image.
The parameters can be adjusted via the sliders (note that the sliders in the GUI
only support integer values, the actual parameters can also be float values).

The border around the image indicates if the smoothed edge mean is below (red)
or above (green) the threshold.

This test is also performed in robot_fingers/trifingerpro_post_submission.py
(the self-test that is run after each job on the TriFingerPro robots).

As argument, the ID of the camera needs to be passed.  Example:

::

    check_camera_sharpness camera180

Additional arguments can be used to set initial values for the parameters.  Run
with ``--help`` to get a complete list.
