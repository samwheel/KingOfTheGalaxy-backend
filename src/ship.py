from dataclasses import dataclass
from typing import TypeAlias

from src.star import Star

SHIP_MODELS = {
    "Scout": {
        "cost": 25,
        "speed": 3,
        "fuel_capacity": 80,
        "fuel_consumption": 1,
        "armor": 5,
        "weapon_power": 3,
        "detection_range": 4,
    },
    "Pioneer": {
        "cost": 50,
        "speed": 2,
        "fuel_capacity": 100,
        "fuel_consumption": 1,
        "armor": 10,
        "weapon_power": 5,
        "detection_range": 5,
    },
}


@dataclass(frozen=True)
class StarLocation:
    star: Star

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.star.coordinates


@dataclass(frozen=True)
class LaneLocation:
    start: Star
    end: Star
    progress: float = 0.0

    def __post_init__(self) -> None:
        if self.end not in self.start.star_lane_connections and self.start not in self.end.star_lane_connections:
            raise ValueError(f"{self.start} and {self.end} are not connected by a star lane")
        if not 0.0 <= self.progress <= 1.0:
            raise ValueError("Lane progress must be between 0.0 and 1.0")

    @property
    def coordinates(self) -> tuple[float, float]:
        start_x, start_y = self.start.coordinates
        end_x, end_y = self.end.coordinates
        return (
            start_x + (end_x - start_x) * self.progress,
            start_y + (end_y - start_y) * self.progress,
        )


ShipLocation: TypeAlias = StarLocation | LaneLocation


class Ship:
    def __init__(self, model_name: str, speed: float, fuel_capacity: float, fuel_consumption: float, armor: float, weapon_power: float, location: ShipLocation, detection_range: float = 4, owner_name: str | None = None):
        self.model_name: str = model_name
        self.speed: float = speed
        self.fuel_capacity: float = fuel_capacity
        self.fuel_consumption: float = fuel_consumption
        self.armor: float = armor
        self.weapon_power: float = weapon_power
        self.location: ShipLocation = location
        self.detection_range: float = detection_range
        self.owner_name: str | None = owner_name
        self.route: list[Star] = []

    def move_to(self, star: Star) -> None:
        if not isinstance(self.location, StarLocation):
            raise ValueError("A ship already traveling on a star lane cannot change course")
        self.set_course([self.location.star, star])

    def set_course(self, path: list[Star]) -> None:
        if not isinstance(self.location, StarLocation):
            raise ValueError("A ship already traveling on a star lane cannot change course")
        if len(path) < 2 or path[0] is not self.location.star:
            raise ValueError("A ship course must begin at the ship's current star")
        for start, end in zip(path, path[1:]):
            if end not in start.star_lane_connections and start not in end.star_lane_connections:
                raise ValueError(f"{start} and {end} are not connected by a star lane")
        self.route = path[2:]
        self.location = LaneLocation(path[0], path[1])

    def advance(self) -> None:
        if not isinstance(self.location, LaneLocation):
            return

        distance = self._distance(self.location.start, self.location.end)
        if distance == 0 or self.speed >= distance * (1 - self.location.progress):
            arrived_at = self.location.end
            if self.route:
                next_star = self.route.pop(0)
                self.location = LaneLocation(arrived_at, next_star)
            else:
                self.location = StarLocation(arrived_at)
            return

        progress_delta = self.speed / distance
        self.location = LaneLocation(
            self.location.start,
            self.location.end,
            self.location.progress + progress_delta,
        )

    @staticmethod
    def _distance(start: Star, end: Star) -> float:
        return ((start.coordinates[0] - end.coordinates[0]) ** 2 + (start.coordinates[1] - end.coordinates[1]) ** 2) ** 0.5

    @property
    def turns_remaining(self) -> int:
        if not isinstance(self.location, LaneLocation):
            return 0
        distance_remaining = self._distance(self.location.start, self.location.end) * (1 - self.location.progress)
        distance_remaining += sum(
            self._distance(start, end)
            for start, end in zip([self.location.end, *self.route], self.route)
        )
        return max(1, int((distance_remaining / self.speed) + 0.999999))

    def to_dict(self) -> dict:
        if isinstance(self.location, StarLocation):
            location = {
                "kind": "star",
                "star": self.location.star.name,
                "coordinates": self.location.coordinates,
            }
        else:
            location = {
                "kind": "lane",
                "start": self.location.start.name,
                "end": self.location.end.name,
                "progress": self.location.progress,
                "coordinates": self.location.coordinates,
                "turns_remaining": self.turns_remaining,
                "route": [self.location.end.name, *(star.name for star in self.route)],
            }

        return {
            "model_name": self.model_name,
            "speed": self.speed,
            "fuel_capacity": self.fuel_capacity,
            "fuel_consumption": self.fuel_consumption,
            "armor": self.armor,
            "weapon_power": self.weapon_power,
            "detection_range": self.detection_range,
            "owner_name": self.owner_name,
            "location": location,
        }