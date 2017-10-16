cmake_minimum_required(VERSION 2.8.8)

project(osrm-test C CXX)

set(BUILD_SHARED_LIBS ON CACHE BOOL "Build shared libs" FORCE)

set(OSRM_INCLUDE_DIR "/usr/local/include" CACHE PATH "Path to OSRM headers directory")
set(OSRM_SHARED_LIB "/usr/local/lib/libosrm.so" CACHE FILEPATH "Path to OSRM shared library")
set(OSRM_LIBBOOST_SHARED_LIB "/usr/lib64/libboost_system.so" CACHE FILEPATH "Path to libboost_system.so")

include_directories(${OSRM_INCLUDE_DIR})
include_directories(${OSRM_INCLUDE_DIR}/osrm)

add_executable(osrm-test main.cpp)

target_link_libraries(osrm-test ${OSRM_SHARED_LIB} ${OSRM_LIBBOOST_SHARED_LIB})


