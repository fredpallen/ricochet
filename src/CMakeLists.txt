cmake_minimum_required (VERSION 2.6)

project (Ricochet)

add_library (ricochet SHARED ricochet.c)

add_executable (main main.c)
target_link_libraries (main ricochet)

# Copy python file to directory with other build products.
configure_file (ricochet.py ricochet.py COPYONLY)
