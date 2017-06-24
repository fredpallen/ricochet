#ifndef JASON_HENLINE_RICOCHET
#define JASON_HENLINE_RICOCHET

#define RICOCHET_BOARD_WIDTH 16
#define RICOCHET_MAX_MOVES 8

#include <stdbool.h>

typedef struct {
    // true means a wall, false means no wall.
    //
    // First index is y, second index is x.

    // Horizontal walls.
    bool horz[RICOCHET_BOARD_WIDTH + 1][RICOCHET_BOARD_WIDTH];

    // Vertical walls.
    bool vert[RICOCHET_BOARD_WIDTH][RICOCHET_BOARD_WIDTH + 1];
} Walls;

typedef struct {
    int x;
    int y;
} Position;

typedef struct {
    int x;
    int y;
} Direction;

typedef struct {
    int length;
    Direction moves[2 * RICOCHET_MAX_MOVES];
} Route;

int get_board_width();
int get_max_moves();

Route find_route(
        const Walls *walls,
        Position start,
        Position end);

#endif  // JASON_HENLINE_RICOCHET
