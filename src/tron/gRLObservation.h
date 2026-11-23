#ifndef G_RL_OBSERVATION_H
#define G_RL_OBSERVATION_H

#include <array>
#include <cstdint>
#include <vector>

namespace RLObservation {

constexpr int GRID_SIZE = 64;
constexpr int CHANNEL_COUNT = 4;

enum class Channel {
    Boundary = 0,
    OwnTrail = 1,
    OpponentTrail = 2,
    OpponentPosition = 3
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

using Grid = std::array<
    std::uint8_t,
    CHANNEL_COUNT * GRID_SIZE * GRID_SIZE
>;

Grid BuildLocalGrid(const Snapshot& state, double cropWidth);

}

#endif