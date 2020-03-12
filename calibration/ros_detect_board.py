#!/usr/bin/env python3
"""ROS node that detects a charuco board in images and publishes the pose."""
from __future__ import print_function, division

import numpy as np

# annoying hack to get the proper version of cv2 (_not_ the ROS one)
import sys
ros_path = "/opt/ros/kinetic/lib/python2.7/dist-packages"
if ros_path in sys.path:
    sys.path.remove(ros_path)
import cv2
sys.path.append(ros_path)

import cv2

import rospy
from geometry_msgs.msg import Pose
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import transformations

from charuco_board import CharucoBoardHandler


class CharucoBoardPosePublisher:

    def __init__(self):
        self.charuco_handler = CharucoBoardHandler()
        self.cv_bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/camera60/image_raw", Image, self.callback)
        self.pose_pub = rospy.Publisher("~pose", Pose, queue_size=100)

    def callback(self, msg):
        cv_image = self.cv_bridge.imgmsg_to_cv2(msg, "bgr8")
        rvec, tvec = self.charuco_handler.detect_board_in_image(cv_image)

        if rvec is not None:
            print("got board")
            # convert the Rodrigues vector to a quaternion
            rotation_matrix = np.array([[0, 0, 0, 0],
                                        [0, 0, 0, 0],
                                        [0, 0, 0, 0],
                                        [0, 0, 0, 1]])
            rotation_matrix[:3, :3] = cv2.Rodrigues(rvec)
            quaternion = transformations.quaternion_from_matrix(rotation_matrix)

            pose = Pose()
            pose.position.x = tvec[0]
            pose.position.y = tvec[1]
            pose.position.z = tvec[2]
            pose.orientation.w = quaternion[0]
            pose.orientation.x = quaternion[1]
            pose.orientation.y = quaternion[2]
            pose.orientation.z = quaternion[3]

            self.pose_pub(pose)
        else:
            print("no board")


def main():
    rospy.init_node("charuco_pose_publisher")

    node = CharucoBoardPosePublisher()  # noqa
    print("init done")
    rospy.spin()


if __name__ == "__main__":
    main()
