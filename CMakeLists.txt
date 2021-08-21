cmake_minimum_required(VERSION 3.14)

project(chessplusplus LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(chessplusplus SHARED
  chessplusplus_global.h
  chessplusplus.cpp
  chessplusplus.h
  constants.h
)

target_compile_definitions(chessplusplus PRIVATE CHESSPLUSPLUS_LIBRARY)
