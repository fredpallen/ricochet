import ctypes

BOARD_WIDTH = 16
MAX_MOVES = 6

WallsRow = BOARD_WIDTH * ctypes.c_int
WallsRows = (BOARD_WIDTH + 1) * WallsRow

WallsCol = (BOARD_WIDTH + 1) * ctypes.c_int
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
            ('moves', MAX_MOVES * Direction),
            ]

if __name__ == '__main__':
    libricochet = ctypes.CDLL('libricochet.so')
    libricochet.find_route.restype = Route
    
    walls = Walls(
            rows=WallsRows(
                WallsRow(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                WallsRow(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                ),
            cols=WallsCols(
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                WallsCol(1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                ))
    start = Position(x=0, y=0)
    end = Position(x=15, y=15)

    route = libricochet.find_route(ctypes.byref(walls), start, end)
    print('route.length =', route.length)
