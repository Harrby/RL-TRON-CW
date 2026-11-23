#ifndef G_RL_OBSERVATION_H
#define G_RL_OBSERVATION_H

#include <array>
#include <cstdint>
#include <vector>
#include "gCycle.h"

class gCycle;

namespace RLObservation {

constexpr int GRID_SIZE = 64;
constexpr int CHANNEL_COUNT = 4;

enum class Channel {
    Boundary = 0, //masks the actual "wall"
    OwnTrail = 1, //masks the agents own trail 
    OpponentTrail = 2, //masks the opponent's trail
    OpponentPosition = 3 //masks the opponent's cycle
};

struct Point {
    double x;
    double y;
};

struct WallSegment {
    Point start;
    Point end;
    Channel channel;  // Boundary, OwnTrail, or OpponentTrail
};

struct Snapshot {
    Point selfPosition;
    Point selfHeading;  // Direction vector, not an angle
    Point opponentPosition;
    bool opponentAlive;

    // Only currently active wall sections.
    std::vector<WallSegment> walls;
};

// Read cycle positions and heading. Wall collection is not included yet
Snapshot ReadCycleState(const gCycle& self, const gCycle* opponent);

using Grid = std::array<
    std::uint8_t,
    CHANNEL_COUNT * GRID_SIZE * GRID_SIZE
>;

Grid BuildLocalGrid(const Snapshot& state, double cropWidth, double forwardOffset);

}

#endif