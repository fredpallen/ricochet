#!/usr/bin/python3

import ctypes
import os

libricochet = ctypes.CDLL(
        os.path.join('@CMAKE_BINARY_DIR@', 'libricochet.so'))
libsimple = ctypes.CDLL(
        os.path.join('@CMAKE_BINARY_DIR@', 'libsimple.so'))

BOARD_WIDTH = libricochet.get_board_width()
MAX_MOVES = libricochet.get_max_moves()

WallsRow = BOARD_WIDTH * ctypes.c_bool
WallsRows = (BOARD_WIDTH + 1) * WallsRow

WallsCol = (BOARD_WIDTH + 1) * ctypes.c_bool
WallsCols = BOARD_WIDTH * WallsCol

BoardVert = (BOARD_WIDTH + 1) * ctypes.c_int
BoardVerts = BOARD_WIDTH * BoardVert
BoardHorz = BOARD_WIDTH * ctypes.c_int
BoardHorzs = (BOARD_WIDTH + 1) * BoardHorz

class Board(ctypes.Structure):
    _fields_ = [('horz', BoardHorzs), ('vert', BoardVerts)]


class Walls(ctypes.Structure):
    _fields_ = [('horz', WallsRows), ('vert', WallsCols)]


class Position(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]

class Move(ctypes.Structure):
    _fields_ = [('robot', ctypes.c_int), ('start', Position), ('end', Position)]

# TODO: Get the value of 4 from the library.
State = 4 * Position

# TODO: Get the value of 20 from the library.
class Solution(ctypes.Structure):
    _fields_ = [('length', ctypes.c_int), ('moves', 20*Move)]

class Direction(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]


class Route(ctypes.Structure):
    _fields_ = [
            ('length', ctypes.c_int),
            ('moves', 2 * MAX_MOVES * Direction),
            ]

class PWalls(object):
    def __init__(self, horz, vert):
        self.horz = horz
        self.vert = vert

    def to_board(self):
        return Board(
                horz=BoardHorzs(
                    *[BoardHorz(
                        *[1 if c else 0 for c in row]
                        ) for row in self.horz]
                    ),
                vert=BoardVerts(
                    *[BoardVert(
                        *[1 if c else 0 for c in row]
                        ) for row in self.vert]
                    )
                )

    @staticmethod
    def from_str(s, width):
        """Makes a PWalls instance from a string representation.

        The string representation uses '|' for vertical wall, '--' for
        horizontal wall, + for cell corner, ' ' for no vertical wall and 2*' '
        for no horizontal wall.

        4x4 example
        '''
        +--+--+--+--+
        |     |     |
        +  +--+--+  +
        |        |  |
        +  +--+  +  +
        |           |
        +  +  +  +  +
        |  |        |
        +--+--+--+--+
        '''
        """
        lines = s.strip().splitlines()
        horz_lines = [line.lstrip() for line in lines[0::2]]
        vert_lines = [line.lstrip() for line in lines[1::2]]
        if len(horz_lines) != width + 1:
            raise Exception('Saw %s horz rows' % len(horz_lines))
        if len(vert_lines) != width:
            raise Exception('Saw %s vert rows' % len(vert_lines))
        horz_chars = [line[1::3] for line in horz_lines]
        vert_chars = [line[0::3] for line in vert_lines]
        for i, chars in enumerate(horz_chars):
            if len(chars) != width:
                raise Exception('Saw %s chars for horz %s' % (len(chars), i))
            if not set(chars).issubset({' ', '-'}):
                raise Exception('Illegal character in horz %s' % i)
        for i, chars in enumerate(vert_chars):
            if len(chars) != width + 1:
                raise Exception('Saw %s chars for vert %s' % (len(chars), i))
            if not set(chars).issubset({' ', '|'}):
                raise Exception('Illegal character in vert %s' % i)
        horz = [[c == '-' for c in chars] for chars in horz_chars]
        vert = [[c == '|' for c in chars] for chars in vert_chars]
        return PWalls(horz=horz, vert=vert)

    def to_str(self):
        width = len(self.vert)
        chars = [(3*width + 1)*[' '] for i in range(2*width+1)]
        for y in range(width + 1):
            for x in range(width + 1):
                chars[2*y][3*x] = '+'
        for y, row in enumerate(self.horz):
            for x, value in enumerate(row):
                if value:
                    chars[2*y][3*x+1] = '-'
                    chars[2*y][3*x+2] = '-'
        for y, row in enumerate(self.vert):
            for x, value in enumerate(row):
                if value:
                    chars[2*y+1][3*x] = '|'
        return '\n'.join([''.join(row) for row in chars]) + '\n'

    def rot90(self):
        width = len(self.vert)
        horz = [width*[False] for i in range(width + 1)]
        vert = [(width + 1)*[False] for i in range(width)]
        for y, row in enumerate(self.horz):
            for x, value in enumerate(row):
                vert[x][width - y] = value
        for y, row in enumerate(self.vert):
            for x, value in enumerate(row):
                horz[x][width - y - 1] = value
        return PWalls(horz=horz, vert=vert)

    def rot180(self):
        return self.rot90().rot90()

    def rot270(self):
        return self.rot90().rot90().rot90()

    def add_section(self, pwalls, xoffset, yoffset):
        width = len(pwalls.vert)
        for y, row in enumerate(pwalls.horz):
            for x, value in enumerate(row):
                self.horz[yoffset + y][xoffset + x] = (
                        self.horz[yoffset + y][xoffset + x] or
                        value)
        for y, row in enumerate(pwalls.vert):
            for x, value in enumerate(row):
                self.vert[yoffset + y][xoffset + x] = (
                        self.vert[yoffset + y][xoffset + x] or
                        value)


def StrToWalls(s):
    """Makes a Walls instance from a string representation.

    The string representation uses '|' for vertical wall, '--' for horizontal
    wall, + for cell corner, ' ' for no vertical wall and 2*' ' for no
    horizontal wall.

    4x4 example
    '''
    +--+--+--+--+
    |     |     |
    +  +--+--+  +
    |        |  |
    +  +--+  +  +
    |           |
    +  +  +  +  +
    |  |        |
    +--+--+--+--+
    '''
    """
    lines = s.strip().splitlines()
    horz_lines = [line.strip() for line in lines[0::2]]
    vert_lines = [line.strip() for line in lines[1::2]]
    if len(horz_lines) != BOARD_WIDTH + 1:
        raise Exception('Saw %s horz rows' % len(horz_lines))
    if len(vert_lines) != BOARD_WIDTH:
        raise Exception('Saw %s vert rows' % len(vert_lines))
    horz_chars = [line[1::3] for line in horz_lines]
    vert_chars = [line[0::3] for line in vert_lines]
    for i, chars in enumerate(horz_chars):
        if len(chars) != BOARD_WIDTH:
            raise Exception('Saw %s chars for horz %s' % (len(chars), i))
        if not set(chars).issubset({' ', '-'}):
            raise Exception('Illegal character in horz %s' % i)
    for i, chars in enumerate(vert_chars):
        if len(chars) != BOARD_WIDTH + 1:
            raise Exception('Saw %s chars for vert %s' % (len(chars), i))
        if not set(chars).issubset({' ', '|'}):
            raise Exception('Illegal character in vert %s' % i)
    horz = WallsRows(
            *[
                WallsRow(*[c == '-' for c in chars])
                for chars in horz_chars
            ])
    vert = WallsCols(
            *[
                WallsCol(*[c == '|' for c in chars])
                for chars in vert_chars
            ])
    return Walls(horz=horz, vert=vert)

EMPTY_QUAD = """
+--+--+--+--+--+--+--+--+
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
"""

# First char:
#   B - Black Hole
#   P - Planet
#   M - Moon
#   S - Star
#   U - Sun
#
# Second char:
#   W - Wild
#   R - Red
#   Y - Yellow
#   G - Green
#   B - Blue

SIMPLE_BLUE_MOON_QUAD = """
+--+--+--+--+--+--+--+--+
|           |            
+  +  +  +  +  +  +  +  +
|                 |UY    
+  +  +  +  +  +  +--+  +
|                        
+--+  +  +  +  +  +  +  +
|            SR|         
+  +  +  +  +--+  +  +  +
|                        
+  +--+  +  +  +  +  +  +
|   MB|                  
+  +  +  +  +  +--+  +  +
|              |PG       
+  +  +  +  +  +  +  +--+
|      BW|           |   
+  +  +--+  +  +  +  +  +
"""

SIMPLE_BLUE_PLANET_QUAD = """
+--+--+--+--+--+--+--+--+
|                    |   
+  +  +  +  +--+  +  +  +
|            MR|         
+--+  +  +  +  +  +  +  +
|                        
+  +--+  +  +  +  +  +  +
|  |UG                   
+  +  +  +  +  +  +  +  +
|                 |PB    
+  +  +  +  +  +  +--+  +
|                        
+  +  +  +  +  +  +  +  +
|         SY|            
+  +  +  +--+  +  +  +--+
|                    |   
+  +  +  +  +  +  +  +  +
"""

SIMPLE_BLUE_STAR_QUAD = """
+--+--+--+--+--+--+--+--+
|                 |      
+  +  +  +--+  +  +  +  +
|         UR|            
+--+  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|                  SB|   
+  +  +  +  +  +  +--+  +
|  |MG                   
+  +--+  +  +  +--+  +  +
|              |PY       
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +--+
|                    |   
+  +  +  +  +  +  +  +  +
"""

SIMPLE_BLUE_SUN_QUAD = """
+--+--+--+--+--+--+--+--+
|           |            
+  +  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +  +
|           |PR          
+  +  +--+  +--+  +  +  +
|     |MY                
+  +  +  +  +  +  +  +  +
|               SG|      
+  +  +  +--+  +--+  +  +
|         UB|            
+--+  +  +  +  +  +  +  +
|                        
+  +  +  +  +  +  +  +--+
|                    |   
+  +  +  +  +  +  +  +  +
"""

BASIC_BOARD = PWalls(
        horz=[BOARD_WIDTH*[False] for i in range(BOARD_WIDTH+1)],
        vert=[(BOARD_WIDTH + 1)*[False] for i in range(BOARD_WIDTH)])
BASIC_BOARD.add_section(PWalls.from_str(SIMPLE_BLUE_MOON_QUAD, 8), 0, 0)
BASIC_BOARD.add_section(PWalls.from_str(SIMPLE_BLUE_PLANET_QUAD, 8).rot90(), 8, 0)
BASIC_BOARD.add_section(PWalls.from_str(SIMPLE_BLUE_STAR_QUAD, 8).rot180(), 8, 8)
BASIC_BOARD.add_section(PWalls.from_str(SIMPLE_BLUE_SUN_QUAD, 8).rot270(), 0, 8)


if __name__ == '__main__':
    libricochet.find_route.restype = Route
    libsimple.solve.restype = Solution

    print(BASIC_BOARD.to_str())

    board = BASIC_BOARD.to_board()
    state = State(
            positions=[
                Position(x=0, y=0),
                Position(x=0, y=1),
                Position(x=0, y=2),
                Position(x=0, y=3)])

    goal = Position(x=3, y=0)
    solution = libsimple.solve(
            ctypes.byref(board),
            ctypes.byref(state),
            0,
            goal)

    if solution.length < 0:
        print('No solution')
    else:
        for i in range(solution.length):
            move = solution.moves[i]
            print(
                    'robot = %s, start = (%s,%s), end = (%s,%s)' % (
                        move.robot,
                        move.start.x,
                        move.start.y,
                        move.end.x,
                        move.end.y))

    walls = StrToWalls(
            """
            +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
            |     |                                         |
            +--+  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +--+  +  +  +  +  +  +  +  +  +  +  +  +
            |  |        |                                   |
            +  +--+  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +--+--+  +  +  +  +  +  +  +
            |                    |     |                    |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                    |     |                    |
            +  +  +  +  +  +  +  +--+--+  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                       |                       |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +--+
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                                               |
            +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +  +
            |                       |                       |
            +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
            """)
    start = Position(x=0, y=0)
    end = Position(x=15, y=15)

    #route = libricochet.find_route(ctypes.byref(walls), start, end)
    #print('route.length =', route.length)
    #for i in range(route.length):
    #    print('x =', route.moves[i].x, ', y = ', route.moves[i].y)
