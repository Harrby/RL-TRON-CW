#include "gRLObservation.h"
#include <cmath>
#include <stdexcept>

namespace RLObservation {

    static Point RelativeToSelf(Point worldPoint, Point selfPosition)
    {
        return Point{
            worldPoint.x - selfPosition.x,
            worldPoint.y - selfPosition.y
        };
    }

    static Point NormaliseHeading(Point heading)
    {
        const double length = std::hypot(heading.x, heading.y);

        if(!std::isfinite(length) || length <= 0.0)
        {
            throw std::invalid_argument("Heading must be finite and non-zero");
        }

        return Point{
            heading.x / length,
            heading.y / length
        };
    }

    // Convert a world point to local coordinates: x = right, y = forward.
    // forward must have length one.
    static Point WorldToLocal(Point worldPoint, Point selfPosition, Point forward)
    {
        const Point relative = RelativeToSelf(worldPoint, selfPosition);

        const double right =
            relative.x * forward.y - relative.y * forward.x;

        const double ahead =
            relative.x * forward.x + relative.y * forward.y;

        return Point{right, ahead};
    }

    // Convert local world units to continuous grid coords
    static Point LocalToGrid(Point localPoint, double cropWidth, double forwardOffset)
    {
        const double cellsPerUnit = GRID_SIZE / cropWidth;
        const double centre = GRID_SIZE / 2.0;

        return Point{
            centre + localPoint.x * cellsPerUnit,
            centre - (localPoint.y - forwardOffset) * cellsPerUnit
        };
    }

    Snapshot ReadCycleState(const gCycle& self, const gCycle* opponent)
    {
        Snapshot state{};

        const auto position = self.Position();
        const auto heading = self.Direction();

        state.selfPosition = Point{position.x, position.y};
        state.selfHeading = Point{heading.x, heading.y};

        if (opponent != nullptr && opponent -> Alive())
        {
            const auto opponentPosition = opponent -> Position();

            state.opponentPosition = Point{
                opponentPosition.x,
                opponentPosition.y
            };
    
            state.opponentAlive = true;
        }

        return state;
    }

    // Build four occupancy layers covering a square of cropWidth world units
    Grid BuildLocalGrid(const Snapshot& state, double cropWidth, double forwardOffset)
    {
        if (!std::isfinite(cropWidth) || cropWidth <= 0.0)
        {
            throw std::invalid_argument("Crop width must be finite and positive");
        }
        
        Grid grid{};

        const Point forward = NormaliseHeading(state.selfHeading);

        if (state.opponentAlive)
        {
            const Point local = WorldToLocal(state.opponentPosition, state.selfPosition, forward);
            const Point cell = LocalToGrid(local, cropWidth, forwardOffset);

            // An opponent outside the crop must not appear on its border
            if (cell.x >= 0.0 && cell.x < GRID_SIZE && cell.y >=0.0 && cell.y < GRID_SIZE)
            {
                const int column = static_cast<int>(std::floor(cell.x));
                const int row = static_cast<int>(std::floor(cell.y));
                const int channel = static_cast<int>(Channel::OpponentPosition);

                const int index = channel * GRID_SIZE * GRID_SIZE + row * GRID_SIZE + column;
                grid[index] = 1;
            }
        }

        return grid;
    }

}