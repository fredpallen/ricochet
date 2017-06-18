#ifndef JASON_HENLINE_RICOCHET
#define JASON_HENLINE_RICOCHET

#define RICOCHET_BOARD_WIDTH 16
#define RICOCHET_MAX_MOVES 6

typedef int Walls[2][RICOCHET_BOARD_WIDTH][RICOCHET_BOARD_WIDTH + 1];

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
    Direction moves[RICOCHET_MAX_MOVES];
} Route;

void find_route(
        const Walls *walls,
        Position start,
        Position end,
        Route *solution);

#endif  // JASON_HENLINE_RICOCHET
