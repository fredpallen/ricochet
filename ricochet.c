#include "ricochet.h"

#include "string.h"

// One route for each cell.
typedef struct {
    Route routes[RICOCHET_BOARD_WIDTH * RICOCHET_BOARD_WIDTH];
} CellRoutes;

typedef struct {
    int indices[RICOCHET_BOARD_WIDTH * RICOCHET_BOARD_WIDTH];
    int length;
} Indices;

static const Direction left = {.x = -1, .y = 0};
static const Direction right = {.x = 1, .y = 0};
static const Direction up = {.x = 0, .y = 1};
static const Direction down = {.x = 0, .y = -1};

static int get_index(Position position) {
    return position.x + position.y * RICOCHET_BOARD_WIDTH;
}

static Position get_position(int index) {
    Position position = {
        .x = index % RICOCHET_BOARD_WIDTH,
        .y = index / RICOCHET_BOARD_WIDTH
    };
    return position;
}

void find_route(
        const Walls *walls,
        Position start,
        Position end,
        Route *route) {
    CellRoutes forward;
    CellRoutes backward;
    memset(&forward, 0, sizeof(forward));
    memset(&backward, 0, sizeof(backward));
    // TODO(fred)
}

static Position move(const Walls *walls, Position start, Direction direction) {
    Position position;
    return position;
    // TODO(fred) Move until the first wall is hit.
}

static void search(
        const Walls *walls,
        Position start,
        CellRoutes *routes) {
    const int start_index = get_index(start);
    routes->routes[start_index].length = 0;

    Direction directions[4] = {
        left,
        right,
        up,
        down,
    };

    Indices indices[2] = {
        {.length = 0},
        {.length = 0}
    };

    Indices *old_indices = &indices[0];
    Indices *new_indices = &indices[1];

    for (int d = 0; d < 4; ++d) {
        int index = get_index(move(walls, start, directions[d]));
        if (index == start_index) {
            continue;
        }
        routes->routes[index].length = 1;
        routes->routes[index].moves[0] = directions[d];
        old_indices->indices[old_indices->length] = index;
        ++old_indices->length;
    }

    for (int m = 1; m < RICOCHET_MAX_MOVES; ++m) {
        for (int i = 0; i < old_indices->length; ++i) {
            int index = old_indices->indices[i];
            Route route = routes->routes[index];
            Direction directions[2];
            if (route.moves[route.length - 1].x) {
                directions[0] = up;
                directions[1] = down;
            } else {
                directions[0] = left;
                directions[1] = right;
            }
            int new_index1 = get_index(
                    move(walls, get_position(index), directions[0]));
            if (new_index1 != start_index &&
                    !routes->routes[new_index1].length) {
                new_indices->indices[new_indices->length] = new_index1;
                ++new_indices->length;
                routes->routes[new_index1] = route;
                routes->routes[new_index1].moves[route.length] = directions[0];
                ++routes->routes[new_index1].length;
            }
            int new_index2 = get_index(
                    move(walls, get_position(index), directions[1]));
            if (new_index2 != start_index &&
                    !routes->routes[new_index2].length) {
                new_indices->indices[new_indices->length] = new_index2;
                ++new_indices->length;
                routes->routes[new_index2] = route;
                routes->routes[new_index2].moves[route.length] = directions[1];
                ++routes->routes[new_index2].length;
            }
        }
        Indices *tmp = old_indices;
        old_indices = new_indices;
        new_indices = tmp;
    }
}
