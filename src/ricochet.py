#!@PYTHON_EXECUTABLE@

from __future__ import print_function

import ctypes
import os
import random

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

class PBoard(object):
    def __init__(self, horz, vert, targets):
        self.horz = horz
        self.vert = vert
        self.targets = targets

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
        """Makes a PBoard instance from a string representation.

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
        # Handle targets
        targets = {}
        for y, row in enumerate(vert_lines):
            for x in range(BOARD_WIDTH):
                cell = row[3*x+1:3*x+3].strip()
                if cell:
                    targets[cell] = (x,y)
        return PBoard(horz=horz, vert=vert, targets=targets)

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
        for target, (x,y) in self.targets.iteritems():
            for i, c in enumerate(target):
                chars[2*y + 1][3*x + 1 + i] = c
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
        # Handle targets.
        targets = {}
        for target, (x,y) in self.targets.iteritems():
            targets[target] = (width - y - 1, x)
        return PBoard(horz=horz, vert=vert, targets=targets)

    def rot180(self):
        return self.rot90().rot90()

    def rot270(self):
        return self.rot90().rot90().rot90()

    def add_section(self, pboard, xoffset, yoffset):
        width = len(pboard.vert)
        for y, row in enumerate(pboard.horz):
            for x, value in enumerate(row):
                self.horz[yoffset + y][xoffset + x] = (
                        self.horz[yoffset + y][xoffset + x] or
                        value)
        for y, row in enumerate(pboard.vert):
            for x, value in enumerate(row):
                self.vert[yoffset + y][xoffset + x] = (
                        self.vert[yoffset + y][xoffset + x] or
                        value)
        # Handle targets.
        for target, (x,y) in pboard.targets.iteritems():
            self.targets[target] = (x + xoffset, y + yoffset)

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

BASIC_BOARD = PBoard(
        horz=[BOARD_WIDTH*[False] for i in range(BOARD_WIDTH+1)],
        vert=[(BOARD_WIDTH + 1)*[False] for i in range(BOARD_WIDTH)],
        targets={})
BASIC_BOARD.add_section(PBoard.from_str(SIMPLE_BLUE_MOON_QUAD, 8), 0, 0)
BASIC_BOARD.add_section(PBoard.from_str(SIMPLE_BLUE_PLANET_QUAD, 8).rot90(), 8, 0)
BASIC_BOARD.add_section(PBoard.from_str(SIMPLE_BLUE_STAR_QUAD, 8).rot180(), 8, 8)
BASIC_BOARD.add_section(PBoard.from_str(SIMPLE_BLUE_SUN_QUAD, 8).rot270(), 0, 8)


if __name__ == '__main__':
    libsimple.solve.restype = Solution

    print(BASIC_BOARD.to_str())

    # Don't allow starting in the center 4 squares.
    illegal_positions = [(3,3), (3,4), (4,3), (4,4)]
    legal_positions = [
            (x,y)
                for x in range(BOARD_WIDTH)
                for y in range(BOARD_WIDTH)
                if (x,y) not in illegal_positions]

    robot = 0
    print('robot = %s' % robot)

    starting_positions = random.sample(legal_positions, ROBOT_COUNT)
    for i, p in enumerate(starting_positions):
        print('Start %s = %s' % (i, p))

    board = BASIC_BOARD.to_board()
    state = State(
                positions=StatePositions(
                    *[Position(x=x, y=y) for (x,y) in starting_positions]))

    for symbol in ['M', 'P', 'S', 'U']:
        for color in ['R', 'Y', 'G', 'B']:
            target = BASIC_BOARD.targets[symbol + color]
            print('target = (%s,%s)' % (target[0], target[1]))
            goal = Position(x=target[0], y=target[1])
            solution = libsimple.solve(
                    ctypes.byref(board),
                    ctypes.byref(state),
                    robot,
                    goal)

            if solution.length < 0:
                print('No solution')
            else:
                print('Solution length =', solution.length)
                for i in range(solution.length):
                    move = solution.moves[i]
                    print(
                            'robot = %s, start = (%s,%s), end = (%s,%s)' % (
                                move.robot,
                                move.start.x,
                                move.start.y,
                                move.end.x,
                                move.end.y))
