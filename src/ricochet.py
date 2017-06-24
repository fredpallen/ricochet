#!/usr/bin/python3

import ctypes
import os

libricochet = ctypes.CDLL(
        os.path.join('@CMAKE_BINARY_DIR@', 'libricochet.so'))

BOARD_WIDTH = libricochet.get_board_width()
MAX_MOVES = libricochet.get_max_moves()

WallsRow = BOARD_WIDTH * ctypes.c_bool
WallsRows = (BOARD_WIDTH + 1) * WallsRow

WallsCol = (BOARD_WIDTH + 1) * ctypes.c_bool
WallsCols = BOARD_WIDTH * WallsCol


class Walls(ctypes.Structure):
    _fields_ = [('rows', WallsRows), ('cols', WallsCols)]


class Position(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]


class Direction(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]


class Route(ctypes.Structure):
    _fields_ = [
            ('length', ctypes.c_int),
            ('moves', 2 * MAX_MOVES * Direction),
            ]

def StrToWalls(s):
    """Makes a Walls instance from a string representation.

    The string representation uses '|' for vertical wall, '=' for horizontal
    wall, + for cell corner, and ' ' for no wall.

    4x4 example
    '''
    +=+=+=+=+
    |   |   |
    + +=+=+ +
    |     | |
    + +=+ + +
    |       |
    + + + + +
    | |     |
    +=+=+=+=+
    '''
    """
    lines = s.strip().splitlines()
    row_lines = [line.strip() for line in lines[0::2]]
    col_lines = [line.strip() for line in lines[1::2]]
    if len(row_lines) != BOARD_WIDTH + 1:
        raise Exception('Saw %s rows' % len(row_lines))
    if len(col_lines) != BOARD_WIDTH:
        raise Exception('Saw %s cols' % len(col_lines))
    row_chars = [line[1::2] for line in row_lines]
    col_chars = [line[0::2] for line in col_lines]
    for i, chars in enumerate(row_chars):
        if len(chars) != BOARD_WIDTH:
            raise Exception('Saw %s chars for rows %s' % (len(chars), i))
        if not set(chars).issubset({' ', '='}):
            raise Exception('Illegal character in rows %s' % i)
    for i, chars in enumerate(col_chars):
        if len(chars) != BOARD_WIDTH + 1:
            raise Exception('Saw %s chars for cols %s' % (len(chars), i))
        if not set(chars).issubset({' ', '|'}):
            raise Exception('Illegal character in cols %s' % i)
    rows = WallsRows(
            *[
                WallsRow(*[c == '=' for c in chars])
                for chars in row_chars
            ])
    cols = WallsCols(
            *[
                WallsCol(*[c == '|' for c in chars])
                for chars in col_chars
            ])
    return Walls(rows=rows, cols=cols)


if __name__ == '__main__':
    libricochet.find_route.restype = Route

    walls = StrToWalls(
            """
            +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
            |   |                           |
            +=+ + + + + + + + + + + + + + + +
            |                               |
            + + + +=+ + + + + + + + + + + + +
            | |     |                       |
            + +=+ + + + + + + + + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |                               |
            + + + + + + + +=+=+ + + + + + + +
            |             |   |             |
            + + + + + + + + + + + + + + + + +
            |             |   |             |
            + + + + + + + +=+=+ + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |               |               |
            + + + + + + + + + + + + + + + +=+
            |                               |
            + + + + + + + + + + + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |                               |
            + + + + + + + + + + + + + + + + +
            |               |               |
            +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
            """)
    start = Position(x=0, y=0)
    end = Position(x=15, y=15)

    route = libricochet.find_route(ctypes.byref(walls), start, end)
    print('route.length =', route.length)
    for i in range(route.length):
        print('x =', route.moves[i].x, ', y = ', route.moves[i].y)
