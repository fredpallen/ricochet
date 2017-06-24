#ifndef JASON_HENLINE_RICOCHET
#define JASON_HENLINE_RICOCHET

#define RICOCHET_BOARD_WIDTH 16
#define RICOCHET_MAX_MOVES 6

typedef struct {
    // Zero means no wall, nonzero means wall.
    int rows[RICOCHET_BOARD_WIDTH + 1][RICOCHET_BOARD_WIDTH];
    int cols[RICOCHET_BOARD_WIDTH][RICOCHET_BOARD_WIDTH + 1];
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
