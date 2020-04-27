*****************
Demo Applications
*****************

Camera Demos
============

Run as follows to use a camera that requires the pylon interface::

    python3 demo_camera.py --pylon

Not passing ``--pylon`` will create a camera object from the system's webcam,
or any other camera connected (if there is one) that can be accessed via just
OpenCV itself.
