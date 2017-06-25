cmake_minimum_required (VERSION 2.6)

project (Ricochet)

add_library (ricochet SHARED ricochet.c)

# Copy python file to directory with other build products.
configure_file (ricochet.py ricochet.py @ONLY)
