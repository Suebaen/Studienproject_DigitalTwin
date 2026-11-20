cmake_minimum_required(VERSION 3.8)
project(jetbot_digitaltwin)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch rviz meshes
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS src/motor_driver_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()