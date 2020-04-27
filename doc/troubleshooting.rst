***************
Troubleshooting
***************

Camera Drivers
==============

Exceptions with Pylon Cameras
-----------------------------

1. In case of a runtime exception, try use a smaller USB 3.0 cable.

2. In case you get the runtime_error::

      Failed to access images from the camera.

   try to disconnect and reconnect the camera first and see if that resolves
   the error.  If it does not, then reduce the image width and height from the
   PylonViewerApp in ``/opt/pylon5/bin``.

3. In case you get a numpy memory error while trying to access the stored
   images, or the error::

      cv2.error: OpenCV(4.2.0) /io/opencv/modules/highgui/src/window.cpp:376:
      error: (-215:Assertion failed) size.width>0 && size.height>0 in function 'imshow'

   while trying to view the image stream, reduce the image width and height
   from the PylonViewerApp.  You can also try reducing the bandwidth in the
   Tools menu in the same app.
