*******************
Using Pylon Cameras
*******************

Install Pylon SDK
=================

1. Get the pylon Camera Software Suite (5.0.12) from `here <https://www.baslerweb.com/en/sales-support/downloads/software-downloads/pylon-5-0-12-linux-x86-64-bit/>`_.
   Then follow the instructions in the INSTALL file of the pylon suite. Pasted
   below for reference (2, 3, 4):

2. Change to the directory which contains this INSTALL file, e.g.::

       cd ~/pylon-5.0.0.1234-x86

3. Extract the corresponding SDK into ``/opt``::

       sudo tar -C /opt -xzf pylonSDK*.tar.gz

4. Install udev rules to set up permissions for basler USB cameras::

       ./setup-usb.sh


Using Pylon in Apptainer
========================

When accessing the cameras from within Apptainer containers, you need to either
install the Pylon SDK in the container, or you can simply bind it from the host system (assuming it's installed there) using

.. code-block:: text

    apptainer shell --bind=/opt/pylon5 container.sif

Note that even if the Pylon SDK is installed in the container, it may be needed
to set up the udev rules on the host system (see last step in the section
above).


.. _pylon_set_device_user_id:

Set Device Name
===============

The Pylon camera drivers in trifinger_cameras expect a unique device name
("DeviceUserID") written to the camera to be able to identify it (especially important
for the :cpp:class:`~trifinger_cameras::TriCameraDriver` where the three cameras need to
be distinguished.

There are two ways to set the name:

1. Using the :ref:`executable_pylon_write_device_user_id_to_camera` command that is
   included in the package.
2. Via the "pylon Viewer" application that is shipped with the Pylon SDK 6 or later
   [1]_.  The "Device User ID" can be modified in the "Device Control" category of the
   camera settings.

Note that after setting a new name, the camera needs to be reset for the change to
become active (either via the pylon Viewer app or by simply unplugging and plugging in
again).

For the TriFinger robots, we use the IDs "camera60", "camera180" and "camera300"
based on their approximate angular position relative to the fingers, see
:ref:`trifinger_docs:finger_and_camera_names`.


Camera Configuration
====================

For configuration of camera settings like frame rate, white balancing, etc., see
:ref:`pylon_settings_file`.


Command Line Tools
==================

This package contains a number of command line tools for general handling of Pylon
cameras:

- :ref:`executable_pylon_list_cameras`
- :ref:`executable_pylon_write_device_user_id_to_camera`
- :ref:`executable_pylon_dump_camera_settings`


.. [1] In version 5, the name will be displayed once set but there doesn't seem to be an
   option to modify it.
