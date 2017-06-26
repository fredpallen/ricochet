#include "simple.h"

#include <queue>
#include <unordered_set>

#ifndef NDEBUG
#include <stdio.h>
#endif

namespace {

enum class Direction {
    UP,
    DOWN,
    LEFT,
    RIGHT
};

constexpr Direction ALL_DIRECTIONS[] = {
    Direction::UP, Direction::DOWN, Direction::LEFT, Direction::RIGHT};

struct Bearing {
    int x;
    int y;

    Bearing(int x, int y) : x(x), y(y) {}
};

Bearing get_bearing(Direction d) {
    switch (d) {
        case Direction::UP:
            return Bearing(0, -1);
        case Direction::DOWN:
            return Bearing(0, 1);
        case Direction::LEFT:
            return Bearing(-1, 0);
        case Direction::RIGHT:
            return Bearing(1, 0);
    }
}

bool is_wall(const Board *board, Position p, Direction d) {
    switch (d) {
        case Direction::UP:
            return board->horz[p.y][p.x];
        case Direction::DOWN:
            return board->horz[p.y + 1][p.x];
        case Direction::LEFT:
            return board->vert[p.y][p.x];
        case Direction::RIGHT:
            return board->vert[p.y][p.x + 1];
    }
}

struct QueueEntry {
    int move_count;
    Move moves[MAX_MOVES];
    State state;

    QueueEntry(int move_count, State state)
        : move_count(move_count), state(state) {}
};

struct HashState {
    size_t operator()(const State &state) const noexcept {
        size_t hash = 5381;
        for (int i = 0; i < ROBOT_COUNT; ++i) {
            hash = (33 * hash) + state.positions[i].x;
            hash = (33 * hash) + state.positions[i].y;
        }
        return hash;
    }
};

}  // namespace

Solution solve(
        const Board *board, const State *state, int robot, Position goal) {
#ifndef NDEBUG
    printf("Searching for solution\n");
    printf("robot = %d\n", robot);
    printf("goal = (%d,%d)\n", goal.x, goal.y);
    for (int i = 0; i < ROBOT_COUNT; ++i) {
        printf(
                "robot %d position = (%d,%d)\n",
                i, state->positions[i].x, state->positions[i].y);
    }
    printf("horz =\n");
    for (int y = 0; y < BOARD_WIDTH + 1; ++y) {
        for (int x = 0; x < BOARD_WIDTH; ++x) {
            printf("%d", board->horz[y][x]);
        }
        printf("\n");
    }
    printf("\n");
    printf("vert =\n");
    for (int y = 0; y < BOARD_WIDTH; ++y) {
        for (int x = 0; x < BOARD_WIDTH + 1; ++x) {
            printf("%d", board->vert[y][x]);
        }
        printf("\n");
    }
    printf("\n");
#endif

    Solution solution;
    solution.length = 0;

    std::unordered_set<State, HashState> seen_states;
    std::queue<QueueEntry> queue;

    if (state->positions[robot] == goal) {
        return solution;
    }

    seen_states.insert(*state);
    queue.emplace(0, *state);

    while (!queue.empty()) {
        QueueEntry entry = queue.front();
        queue.pop();
        for (int r = 0; r < ROBOT_COUNT; ++r) {
            for (Direction d : ALL_DIRECTIONS) {
                Position cursor = entry.state.positions[r];
                Bearing bearing = get_bearing(d);
                while (!is_wall(board, cursor, d)) {
                    cursor.x += bearing.x;
                    cursor.y += bearing.y;
                    // Check for hitting a robot.
                    // TODO: Is there a better way to do this?
                    bool hit_robot = false;
                    for (int i = 0; i < ROBOT_COUNT; ++i) {
                        if ((i != r) && (cursor == entry.state.positions[i])) {
                            cursor.x -= bearing.x;
                            cursor.y -= bearing.y;
                            hit_robot = true;
                            break;
                        }
                    }
                    if (hit_robot) {
                        break;
                    }
                }
#ifndef NDEBUG
                printf("robot = %d, end state = (%d,%d)\n", r, cursor.x, cursor.y);
#endif
                State end = entry.state;
                end.positions[r] = cursor;

                if (seen_states.count(end)) {
                    continue;
                }
                seen_states.insert(end);

                QueueEntry new_entry = entry;
                new_entry.state.positions[r] = cursor;
                new_entry.moves[new_entry.move_count] =
                    Move(r, entry.state.positions[r], cursor);
                ++new_entry.move_count;

                if ((r == robot) && (cursor == goal)) {
                    solution.length = new_entry.move_count;
                    for (int i = 0; i < new_entry.move_count; ++i) {
                        solution.moves[i] = new_entry.moves[i];
                    }
                    return solution;
                }
                queue.push(new_entry);
            }
        }
    }

    solution.length = -1;
    return solution;
}
