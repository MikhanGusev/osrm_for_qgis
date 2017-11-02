cmake_minimum_required(VERSION 2.8.8)

project(osrm-test)

set(BUILD_SHARED_LIBS ON CACHE BOOL "Build shared libs" FORCE)

set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})

find_package(Boost COMPONENTS system REQUIRED)
find_package(LibOSRM REQUIRED)

include_directories(${LibOSRM_INCLUDE_DIR})
include_directories(${LibOSRM_INCLUDE_DIR}/osrm)
include_directories(${Boost_INCLUDE_DIRS})

add_executable(osrm-test main.cpp)

target_link_libraries(osrm-test ${LibOSRM_LIBRARIES} ${Boost_LIBRARIES})
