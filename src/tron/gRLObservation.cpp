#include "gRLObservation.h"

namespace RLObservation {

    static Point RelativeToSelf(Point worldPoint, Point selfPosition)
    {
        return Point{
            worldPoint.x - selfPosition.x,
            worldPoint.y - selfPosition.y
        };
    }

    Grid BuildLocalGrid(const Snapshot& state, double cropWidth)
    {
        Grid grid{};


        return grid;
    }

}