#define ROBOT_COUNT 4
#define BOARD_WIDTH 16
#define MAX_MOVES 20

typedef struct Position {
    int x;
    int y;

#ifdef __cplusplus
    Position() {}
    Position(int x, int y) : x(x), y(y) {}

    bool operator==(const Position &that) const {
        return this->x == that.x && this->y == that.y;
    }

    bool operator!=(const Position &that) const {
        return !(*this == that);
    }
#endif
} Position;

typedef struct Move {
    int robot;
    Position start;
    Position end;

#ifdef __cplusplus
    Move() {}

    Move(int robot, Position start, Position end)
        : robot(robot), start(start), end(end) {}
#endif
} Move;

typedef struct State {
    Position positions[ROBOT_COUNT];

#ifdef __cplusplus
    bool operator==(const State &that) const {
        for (int i = 0; i < ROBOT_COUNT; ++i) {
            if (this->positions[i] != that.positions[i]) {
                return false;
            }
        }
        return true;
    }
#endif
} State;

typedef struct Board {
    int horz[BOARD_WIDTH + 1][BOARD_WIDTH];
    int vert[BOARD_WIDTH][BOARD_WIDTH + 1];
} Board;

typedef struct Solution {
    int length;
    Move moves[MAX_MOVES];

#ifdef __cplusplus
    Solution() : length(0) {}
#endif
} Solution;

#ifdef __cplusplus
extern "C" {
#endif

int get_board_width();
int get_max_moves();
int get_robot_count();

Solution solve(
        const Board *board, const State *state, int robot, Position goal);

#ifdef __cplusplus
}  // extern "C"
#endif
