Calibration of Extrinsic Camera Parameters
==========================================

The extrinsic camera parameters describe the pose of the camera in the world.
That is, what we are looking for is the transformation from the /base_link
frame to the camera frame.

We do this, using a Charuco board.  When detecting the board in the images of
the camera, we get the transformation from the camera frame to the board frame.
When we know the transformation between the board frame and /base_link, we can
compute /base_link to /camera from this.
In the simplest case the board is placed such that the board frame matches
exactly with /base_link.  In this case we only need to invert the "camera to
board" transformation that we get from the detection.

There are two scripts assisting with this:

- `charuco_board.py detect_image --filename image.png --no-gui` detects the
  board in a save image and outputs its pose as a JSON string containing "rvec"
  and "tvec" as they are returned from OpenCV's detection function.
- `convert_to_camera_pose.py` takes as argument the JSON string with the board
  pose and outputs the "board to camera" in the format `x y z qx qy qz qw`
  (i.e. the format that is used by `static_transform_publisher`).  If the board
  was place such that its origin matches /base_link, this can directly be used
  for a "base_link to camera" transform publisher.

Example usage combining the two scripts in one call:

    rosrun trifinger_cameras convert_to_camera_pose.py \
        "$(rosrun trifinger_cameras charuco_board.py detect_image \
            --filename path/to/image.png --no-gui)"
