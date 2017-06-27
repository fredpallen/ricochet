#!@PYTHON_EXECUTABLE@

from __future__ import print_function

import ctypes
import os

libsimple = ctypes.CDLL(
        os.path.join('@CMAKE_BINARY_DIR@', 'libsimple.so'))

BOARD_WIDTH = libsimple.get_board_width()
MAX_MOVES = libsimple.get_max_moves()
ROBOT_COUNT = libsimple.get_robot_count()

BoardHorz = BOARD_WIDTH * ctypes.c_int
BoardHorzs = (BOARD_WIDTH + 1) * BoardHorz
BoardVert = (BOARD_WIDTH + 1) * ctypes.c_int
BoardVerts = BOARD_WIDTH * BoardVert

class Board(ctypes.Structure):
    _fields_ = [('horz', BoardHorzs), ('vert', BoardVerts)]

class Position(ctypes.Structure):
    _fields_ = [('x', ctypes.c_int), ('y', ctypes.c_int)]

class Move(ctypes.Structure):
    _fields_ = [('robot', ctypes.c_int), ('start', Position), ('end', Position)]

StatePositions = ROBOT_COUNT * Position
class State(ctypes.Structure):
    _fields_ = [('positions', StatePositions)]

class Solution(ctypes.Structure):
    _fields_ = [('length', ctypes.c_int), ('moves', MAX_MOVES*Move)]

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
    libsimple.solve.restype = Solution

    print(BASIC_BOARD.to_str())

    board = BASIC_BOARD.to_board()
    state = State(
                positions=StatePositions(
                    Position(x=0, y=0),
                    Position(x=0, y=1),
                    Position(x=0, y=2),
                    Position(x=0, y=3)))

    goal = Position(x=12, y=14)
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
