cmake_minimum_required (VERSION 3.1)

project (Ricochet)

set (CMAKE_CXX_STANDARD 11)

add_library (split_maze SHARED split_maze.c)
add_library (simple SHARED simple.cc)

# Copy python file to directory with other build products.
find_package(PythonInterp 2.7 REQUIRED)

configure_file (ricochet.py ricochet.py @ONLY)
