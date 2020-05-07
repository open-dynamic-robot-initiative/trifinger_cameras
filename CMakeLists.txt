cmake_minimum_required(VERSION 2.8.3)
project(trifinger_cameras)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

find_package(catkin REQUIRED
    roslib
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

catkin_package(
    LIBRARIES
        opencv_driver
        pylon_driver
        tricamera_driver
)


include_directories(
    include
    ${catkin_INCLUDE_DIRS}
    ${Pylon_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
)


# Libraries
add_library(opencv_driver src/opencv_driver.cpp)
target_link_libraries(opencv_driver ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})

add_library(pylon_driver src/pylon_driver.cpp)
target_link_libraries(pylon_driver
    ${catkin_LIBRARIES} ${OpenCV_LIBRARIES} ${Pylon_LIBRARIES})

add_library(tricamera_driver src/tricamera_driver.cpp)
target_link_libraries(tricamera_driver pylon_driver)


# Python Bindings
catkin_add_pybind11_module(py_camera_types opencv_driver pylon_driver)
catkin_add_pybind11_module(py_tricamera_types tricamera_driver)


# Installation
install(DIRECTORY include/${PROJECT_NAME}/
        DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION})

install(DIRECTORY config/
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config)

install(
    TARGETS opencv_driver pylon_driver tricamera_driver
    ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
    LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
    RUNTIME DESTINATION ${CATKIN_GLOBAL_BIN_DESTINATION}
)


# Tests
if (CATKIN_ENABLE_TESTING)
    catkin_add_gtest(test_serialize_cvmat tests/test_serialize_cvmat.cpp)
    target_link_libraries(test_serialize_cvmat
        ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})

    catkin_add_gtest(test_camera_observation tests/test_camera_observation.cpp)
    target_link_libraries(test_camera_observation
        ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})

    catkin_add_gtest(test_shared_memory_camera_data
        tests/test_shared_memory_camera_data.cpp)
    target_link_libraries(test_shared_memory_camera_data
        ${catkin_LIBRARIES} ${OpenCV_LIBRARIES} rt) # FIXME why is "rt" needed?
endif()
