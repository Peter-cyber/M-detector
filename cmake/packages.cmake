list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

# glog
find_package(Glog REQUIRED)
include_directories(${Glog_INCLUDE_DIRS})

# find_package(catkin REQUIRED COMPONENTS
#         geometry_msgs
#         nav_msgs
#         sensor_msgs
#         roscpp
#         rospy
#         std_msgs
#         pcl_ros
#         tf
#         message_generation
#         )


# add_message_files(
#         FILES
#         Pose6D.msg
# )

# generate_messages(
#         DEPENDENCIES
#         geometry_msgs
# )
# catkin_package(
#         CATKIN_DEPENDS geometry_msgs nav_msgs roscpp rospy std_msgs message_runtime
#         DEPENDS EIGEN3 PCL
#         INCLUDE_DIRS
# )


find_package(Eigen3 REQUIRED)
find_package(PCL 1.8 REQUIRED)
find_package(yaml-cpp REQUIRED)

include_directories(
        ${catkin_INCLUDE_DIRS}
        ${EIGEN3_INCLUDE_DIR}
        ${PCL_INCLUDE_DIRS}
        ${PYTHON_INCLUDE_DIRS}
        ${yaml-cpp_INCLUDE_DIRS}
        include
)
