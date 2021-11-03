cmake_minimum_required(VERSION 3.14)

project(chessplusplus LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(include/chessplusplus)
add_subdirectory(private)
add_subdirectory(test)
