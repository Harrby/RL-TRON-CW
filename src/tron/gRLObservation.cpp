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

    Snapshot ReadCycleState(const gCycle& self, const gCycle* opponent)
    {
        Snapshot state{};

        cosnt auto position = self.Position();
        const auto heading = self.Direction();

        state.selfPosition = Point{position.x, position.y}
        state.selfHeading = Point{heading.x, heading.y}

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
    Grid BuildLocalGrid(const Snapshot& state, double cropWidth)
    {
        Grid grid{};


        return grid;
    }

}