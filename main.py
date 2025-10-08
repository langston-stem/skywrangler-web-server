import json
from qgc_mission import QgcJSONEncoder
from sw_mission import create_mission
from sw_mission.points import Coordinate2D, Parameters, Point, Transect


if __name__ == "__main__":
    plan = create_mission(
        launch=Point(
            latitude=35.9301904295499, longitude=-97.26450295241108, altitude=307
        ),
        origin=Point(
            latitude=35.932121645130756, longitude=-97.2631249266781, altitude=304
        ),
        transect=Transect(azimuth=-85, length=100),
        parameters=Parameters(speed=5, angle=90, distance=30),
        return_point=Coordinate2D(
            latitude=35.934456813161006, longitude=-97.2646272318608
        ),
    )

    with open("test.plan", "w") as f:
        json.dump(plan, f, cls=QgcJSONEncoder, indent=4)
