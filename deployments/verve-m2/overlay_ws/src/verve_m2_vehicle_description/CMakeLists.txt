cmake_minimum_required(VERSION 3.5)
project(verve_m2_vehicle_description)

find_package(ament_cmake_auto REQUIRED)

ament_auto_find_build_dependencies()

ament_auto_package(INSTALL_TO_SHARE
  mesh
  urdf
  config
)
