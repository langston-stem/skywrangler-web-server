import json
from typing import TypedDict
from qgc_mission import QgcJSONEncoder
from sw_mission import create_mission
from sw_mission.points import Coordinate2D, Parameters, Point, Transect


class MissionData(TypedDict):
    home: dict[str, float]
    origin: dict[str, float]
    transect: dict[str, float]
    away: dict[str, float]
    variables: dict[str, list[float]]


if __name__ == "__main__":
    with open("mission-data.json", "r") as f:
        mission_data = json.load(f)

    for speed in mission_data["variables"]["speed"]:
        for angle in mission_data["variables"]["angle"]:
            for distance in mission_data["variables"]["distance"]:

                plan = create_mission(
                    launch=Point(
                        latitude=mission_data["home"]["latitude"],
                        longitude=mission_data["home"]["longitude"],
                        altitude=mission_data["home"]["altitude"],
                    ),
                    origin=Point(
                        latitude=mission_data["origin"]["latitude"],
                        longitude=mission_data["origin"]["longitude"],
                        altitude=mission_data["origin"]["altitude"],
                    ),
                    transect=Transect(
                        azimuth=mission_data["transect"]["azimuth"],
                        length=mission_data["transect"]["length"],
                    ),
                    parameters=Parameters(speed=speed, angle=angle, distance=distance),
                    return_point=Coordinate2D(
                        latitude=mission_data["away"]["latitude"],
                        longitude=mission_data["away"]["longitude"],
                    ),
                )

                with open(f"skywrangler_s{speed}_a{angle}_d{distance}.plan", "w") as f:
                    json.dump(plan, f, cls=QgcJSONEncoder, indent=4)
