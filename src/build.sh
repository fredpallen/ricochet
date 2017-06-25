#!/bin/bash

gcc -c -Wall -Wextra main.c
g++ -std=c++11 -c -Wall -Wextra simple.cc
g++ -o main main.o simple.o
