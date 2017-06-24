#include "ricochet.h"

#include <assert.h>
#include <stdbool.h>
#include <string.h>

static const Direction left = {.x = -1, .y = 0};
static const Direction right = {.x = 1, .y = 0};
static const Direction up = {.x = 0, .y = 1};
static const Direction down = {.x = 0, .y = -1};

static const Direction directions[4] = {
    {.x = -1, .y = 0},
    {.x = 1, .y = 0},
    {.x = 0, .y = 1},
    {.x = 0, .y = -1},
};

typedef struct {
    bool seen;
    Route route;
} CellState;

typedef struct {
    CellState states[RICOCHET_BOARD_WIDTH][RICOCHET_BOARD_WIDTH];
} CellStates;

static Direction rot90(Direction d) {
    Direction result = {.x = -d.y, .y = d.x}; 
    return result;
}

static Direction rot180(Direction d) {
    Direction result = {.x = -d.x, .y = -d.y};
    return result;
}

static Direction rot270(Direction d) {
    Direction result = {.x = d.y, .y = -d.x};
    return result;
}

static int is_same_direction(Direction d1, Direction d2) {
    return d1.x == d2.x && d1.y == d2.y;
}

static int is_wall(
        const Walls *walls,
        Position p,
        Direction d) {
    if (is_same_direction(d, left)) {
        return walls->rows[p.x][p.y];
    } else if (is_same_direction(d, right)) {
        return walls->rows[p.x + 1][p.y];
    } else if (is_same_direction(d, up)) {
        return walls->cols[p.x][p.y + 1];
    } else if (is_same_direction(d, down)) {
        return walls->cols[p.x][p.y];
    } else {
        return 1;
    }
}

static void search_forward(
        CellStates *states,
        const Walls *walls,
        Position start,
        int level) {
    if (!level) {
        return;
    }
    const Route route = states->states[start.x][start.y].route;
    const int length = route.length;
    for (int i = 0; i < 4; ++i) {
        Position cursor = start;
        Direction d = directions[i];
        while(!is_wall(walls, cursor, d)) {
            cursor.x += d.x;
            cursor.y += d.y;
        }
        CellState *state = &states->states[cursor.x][cursor.y];
        int is_new = !state->seen || state->route.length > length + 1;
        if (is_new) {
            state->seen = 1;
            state->route = route;
            state->route.moves[route.length] = d;
            ++state->route.length;
            search_forward(states, walls, cursor, level - 1);
        }
    }
}

// Assumes is_wall(walls, start, rot180(dir)) so that we're searching
// backward from a place we could actually stop.
static void search_backward(
        CellStates *states,
        const Walls *walls,
        Position start,
        Direction dir,
        int level) {
    assert(is_wall(walls, start, rot180(dir)));
    if (!level) {
        return;
    }
    const Route route = states->states[start.x][start.y].route;
    const int length = route.length;
    Position cursor = start;
    while (!is_wall(walls, cursor, dir)) {
        cursor.x += dir.x;
        cursor.y += dir.y;
        CellState *state = &states->states[cursor.x][cursor.y];
        // Don't continue states that we have reached with fewer moves.
        if (state->seen && state->route.length <= length) {
            continue;
        }
        Direction d90 = rot90(dir);
        Direction d270 = rot270(dir);
        bool is_wall_d90 = is_wall(walls, cursor, d90);
        bool is_wall_d270 = is_wall(walls, cursor, d270);
        if (is_wall_d90 || is_wall_d270) {
            state->seen = true;
            state->route = route;
            state->route.moves[route.length] = dir;
            ++state->route.length;
        }
        if (is_wall_d90) {
            search_backward(states, walls, cursor, d270, level - 1);
        } else if (is_wall_d270) {
            search_backward(states, walls, cursor, d90, level - 1);
        }
    }
}

Route find_route(
        const Walls *walls,
        Position start,
        Position end) {
    Route route;
    CellStates forward;
    CellStates backward;

    memset(&forward, 0, sizeof(forward));
    memset(&backward, 0, sizeof(backward));

    forward.states[start.x][start.y].seen = true;
    forward.states[start.x][start.y].route.length = 0;

    backward.states[end.x][end.y].seen = true;
    backward.states[end.x][end.y].route.length = 0;

    search_forward(&forward, walls, start, RICOCHET_MAX_MOVES);

    // Only search backward along a direction if there is a wall in the
    // other direction.
    for (int i = 0; i < 4; ++i) {
        Direction d = directions[i];
        if (is_wall(walls, end, d)) {
            search_backward(
                    &backward, walls, end, rot180(d), RICOCHET_MAX_MOVES);
        }
    }

    route.length = 2 * RICOCHET_BOARD_WIDTH + 2;
    for (int x = 0; x < RICOCHET_BOARD_WIDTH; ++x) {
        for (int y = 0; y < RICOCHET_BOARD_WIDTH; ++y) {
            CellState f = forward.states[x][y];
            CellState b = backward.states[x][y];
            if (f.seen && b.seen &&
                    (f.route.length + b.route.length < route.length)) {
                route = f.route;
                route.length = f.route.length + b.route.length;
                for (int i = 0; i < b.route.length; ++i) {
                    route.moves[f.route.length + i].x =
                        -b.route.moves[b.route.length - 1 - i].x;
                    route.moves[f.route.length + i].y =
                        -b.route.moves[b.route.length - 1 - i].y;
                }
            }
        }
    }
    if (route.length == 2 * RICOCHET_BOARD_WIDTH + 2) {
        route.length = -1;
    }
    return route;
}

int get_board_width() {
    return RICOCHET_BOARD_WIDTH;
}

int get_max_moves() {
    return RICOCHET_MAX_MOVES;
}
