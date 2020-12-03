#!/usr/bin/env python3
import cv2


def main():
    # ArUco stuff
    marker_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)

    cap = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        marker_corners, ids, _ = cv2.aruco.detectMarkers(frame, marker_dict)
        print(ids)

        image = cv2.aruco.drawDetectedMarkers(frame, marker_corners, ids)
        cv2.imshow("Aruco", image)
        cv2.waitKey(5)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
