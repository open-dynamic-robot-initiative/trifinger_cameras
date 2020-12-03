cmake_minimum_required(VERSION 3.5)
project(trifinger_cameras)

set(CMAKE_CXX_STANDARD 17)

# libraries need to be position independent for building Python modules
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(mpi_cmake_modules REQUIRED)
find_package(pybind11 REQUIRED)
find_package(cereal REQUIRED)
find_package(robot_interfaces REQUIRED)
find_package(serialization_utils REQUIRED)
find_package(yaml_utils REQUIRED)
find_package(sensor_msgs REQUIRED)

find_package(Eigen3 REQUIRED)
find_package(OpenCV REQUIRED)

find_package(Pylon)
if (${Pylon_FOUND})
    add_definitions(-DPylon_FOUND)
    ament_export_dependencies(Pylon)
endif()


ament_python_install_package(${PROJECT_NAME} PACKAGE_DIR python/${PROJECT_NAME})


ament_export_interfaces(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)


# Libraries
add_library(camera_observations
    src/camera_observation.cpp
    src/tricamera_observation.cpp
)
target_include_directories(camera_observations PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${OpenCV_INCLUDE_DIRS})
target_link_libraries(camera_observations
    ${OpenCV_LIBRARIES}
    serialization_utils::serialization_utils
)


add_library(opencv_driver src/opencv_driver.cpp)
target_include_directories(opencv_driver PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${OpenCV_INCLUDE_DIRS}
)
target_link_libraries(opencv_driver
    ${OpenCV_LIBRARIES}
    robot_interfaces::robot_interfaces
    camera_observations
)


if (${Pylon_FOUND})
    add_library(pylon_driver src/pylon_driver.cpp)
    target_include_directories(pylon_driver PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
        ${OpenCV_INCLUDE_DIRS}
        ${Pylon_INCLUDE_DIRS}
    )
    target_link_libraries(pylon_driver
        ${OpenCV_LIBRARIES}
        ${Pylon_LIBRARIES}
        robot_interfaces::robot_interfaces
        camera_observations
    )
    ament_target_dependencies(pylon_driver
        ament_index_cpp
    )


    add_library(tricamera_driver src/tricamera_driver.cpp)
    target_include_directories(tricamera_driver PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
        ${OpenCV_INCLUDE_DIRS}
        ${Pylon_INCLUDE_DIRS}
    )
    target_link_libraries(tricamera_driver
        ${OpenCV_LIBRARIES}
        ${Pylon_LIBRARIES}
        robot_interfaces::robot_interfaces
        pylon_driver
    )


    # Set library names to variables, so we can use the variable instead of the
    # direct name below.  In case, Pylon drivers are not built, the variables
    # will be empty and thus not cause trouble when used for linking etc.
    set(pylon_driver pylon_driver)
    set(tricamera_driver tricamera_driver)
endif()


add_library(pybullet_tricamera_driver src/pybullet_tricamera_driver.cpp)
target_include_directories(pybullet_tricamera_driver PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(pybullet_tricamera_driver
    camera_observations
    serialization_utils::serialization_utils
    robot_interfaces::robot_interfaces
)


add_library(camera_calibration_parser
    src/parse_yml.cpp
    src/camera_parameters.cpp
)
target_include_directories(camera_calibration_parser PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(camera_calibration_parser yaml_utils::yaml_utils)
ament_target_dependencies(camera_calibration_parser
    sensor_msgs
)


add_executable(load_camera_config_test src/load_camera_config_test.cpp)
target_include_directories(load_camera_config_test PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(load_camera_config_test camera_calibration_parser)
ament_target_dependencies(load_camera_config_test sensor_msgs)


# Python Bindings
add_pybind11_module(py_camera_types srcpy/py_camera_types.cpp
    LINK_LIBRARIES
        camera_observations
        opencv_driver
        ${pylon_driver}
)
add_pybind11_module(py_tricamera_types srcpy/py_tricamera_types.cpp
    LINK_LIBRARIES
        ${OpenCV_LIBRARIES}
        ${tricamera_driver}
        pybullet_tricamera_driver
)


# Installation
install(DIRECTORY include/${PROJECT_NAME}/
        DESTINATION include/${PROJECT_NAME})

install(DIRECTORY config/
        DESTINATION share/${PROJECT_NAME}/config)

install(FILES cmake/FindPylon.cmake
        DESTINATION share/${PROJECT_NAME}/cmake)

install(
    TARGETS
        ${pylon_driver}
        ${tricamera_driver}
        camera_calibration_parser
        camera_observations
        opencv_driver
        pybullet_tricamera_driver
    EXPORT export_${PROJECT_NAME}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install_scripts(
    scripts/analyze_tricamera_log.py
    scripts/calibrate_cameras.py
    scripts/calibrate_trifingerpro_cameras.py
    scripts/camera_log_viewer.py
    scripts/charuco_board.py
    scripts/convert_to_camera_pose.py
    scripts/detect_aruco_marker.py
    scripts/overlay_camera_stream.py
    scripts/record_image_dataset.py
    scripts/tricamera_log_converter.py
    scripts/tricamera_log_viewer.py
    scripts/tricamera_test_connection.py
    scripts/verify_calibration.py

    DESTINATION lib/${PROJECT_NAME}
)


# Tests
if (BUILD_TESTING)
    find_package(ament_cmake_gtest REQUIRED)
    find_package(ament_cmake_nose REQUIRED)

    # install files that are used by the tests
    install(FILES tests/camera_calib.yml
            DESTINATION share/${PROJECT_NAME}/tests)

    ament_add_gtest(test_camera_observation tests/test_camera_observation.cpp)
    target_link_libraries(test_camera_observation
        ${OpenCV_LIBRARIES}
        camera_observations
    )

    ament_add_gtest(test_shared_memory_camera_data
        tests/test_shared_memory_camera_data.cpp)
    target_link_libraries(test_shared_memory_camera_data
        ${OpenCV_LIBRARIES}
        robot_interfaces::robot_interfaces
        camera_observations
    )

    ament_add_nose_test(test_utils tests/test_utils.py)
    ament_add_nose_test(test_camera_calibration_file
        tests/test_camera_calibration_file.py)
endif()



ament_export_include_directories(include ${Pylon_INCLUDE_DIRS})
ament_export_libraries(
    camera_observations
    opencv_driver
    ${pylon_driver}
    ${tricamera_driver}
    pybullet_tricamera_driver
    camera_calibration_parser
)
ament_export_dependencies(yaml_utils)
ament_package(CONFIG_EXTRAS cmake/cfg_extras.cmake.in)
