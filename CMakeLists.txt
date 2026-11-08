
cmake_minimum_required(VERSION 3.30)

project(parallel_lab LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(MPI REQUIRED COMPONENTS CXX)

add_executable(matrix main.cpp)

target_link_libraries(matrix PRIVATE MPI::MPI_CXX)

target_compile_options(matrix PRIVATE
    -Wall
    -Wextra
    -Wpedantic
)
