cmake_minimum_required(VERSION 2.8.3)
project(trifinger_cameras)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

find_package(catkin REQUIRED
    pybind11_catkin
    robot_interfaces
)

find_package(OpenCV REQUIRED)

find_package(Pylon)
if (${Pylon_FOUND})
    add_definitions(-DPylon_FOUND)
endif()

search_for_eigen()


catkin_python_setup()

catkin_package()


include_directories(
    include
    ${catkin_INCLUDE_DIRS}
    ${Pylon_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
)


# Python Bindings
catkin_add_pybind11_module(py_camera_types
    ${OpenCV_LIBRARIES} ${Pylon_LIBRARIES})
catkin_add_pybind11_module(py_tricamera_types
    ${OpenCV_LIBRARIES} ${Pylon_LIBRARIES})
