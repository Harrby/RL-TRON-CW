#ifndef RL_CONFIG_H
#define RL_CONFIG_H 

#define PI 3.14159265358979323846 

// Constants
namespace RLConfig {
    const float RAY_SIZE = 50.0;                      // The length of the raycast sensors for the agent
    const int N_RAYS = 16;                            // The number of raycast sensors used.
    const float FAN_ANGLE = PI*2.0;                   // The range the sensors will be distributed at.
    constexpr double LOCAL_GRID_WIDTH = 16.0;         // The actual width and height of the grid in world units (provisional)
    constexpr double LOCAL_GRID_FORWARD_OFFSET = 4.0; // Offset of the local grid centre ahead of the cycle (in world units).

    constexpr bool DEBUG_DRAW_LOCAL_GRID = true;      // Enable drawing the local observation grid in-game
    constexpr bool DEBUG_DRAW_RAYS = true;           // Enable drawing the raycast sensors in-game
    constexpr float DEBUG_GRID_HEIGHT = 4.0f;
}

#endif