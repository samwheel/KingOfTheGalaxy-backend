from src.planet import Planet
from random import Random

class Empire:
    def __init__(self, name: str, color: str, planets: list[Planet] | None = None, random_generator: Random | None = None):
        self.name: str = name
        self.color: str = color.lower()
        self.planets: list[Planet] = planets if planets is not None else []
        self.detectable_region: list[dict] = []
        self.production: dict[str, float] = {"population": 0.2, "revenue": 0.2, "research": 0.2, "defense": 2, "detection_range": 2}
        self.money: float = 0
        self.max_population_bonus: float = 10
        self.random_generator: Random = random_generator if random_generator is not None else Random()

    def __str__(self) -> str:
        return self.name

    def update_detectable_region(self, starmap: list, ships: list | None = None) -> None:
        planet_names = {planet.name for planet in self.planets}
        self.detectable_region = [
            {
                "center": star.coordinates,
                "radius": planet.statistics["detection_range"],
            }
            for star in starmap
            if any(planet.name in planet_names for planet in star.planets)
            for planet in star.planets
            if planet.name in planet_names
        ]
        self.detectable_region.extend(
            {
                "center": ship.location.coordinates,
                "radius": ship.detection_range,
            }
            for ship in ships or []
            if ship.owner_name == self.name
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "planets": [planet.name for planet in self.planets],
            "detectable_region": self.detectable_region,
            "production": self.production,
            "money": self.money
        }

    def _find_best_planet(self, starmap: list) -> Planet | None:
        owned_planet_names = {planet.name for planet in self.planets}
        best_planet = None
        best_distance = float('inf')
        for star in starmap:
            if not star.planets:
                continue
            for planet in star.planets:
                if planet.name in owned_planet_names:
                    continue

                in_detectable_region = any(
                    (star.coordinates[0] - region["center"][0]) ** 2
                    + (star.coordinates[1] - region["center"][1]) ** 2
                    <= region["radius"] ** 2
                    for region in self.detectable_region
                )
                if not in_detectable_region:
                    continue

                distance = min(
                    ((star.coordinates[0] - region["center"][0]) ** 2
                    + (star.coordinates[1] - region["center"][1]) ** 2) ** 0.5
                    for region in self.detectable_region
                )
                if distance < best_distance:
                    best_distance = distance
                    best_planet = planet

        return best_planet
                

    def turn_update(self, starmap: list) -> None:
        for planet in self.planets:
            planet.statistics["population"] += planet.statistics["population"] * self.production["population"]
            if planet.statistics["population"] > self.max_population_bonus:
                planet.statistics["population"] = self.max_population_bonus

                if self.random_generator.randint(0, 20) == 0:
                    best_planet = self._find_best_planet(starmap)
                    if best_planet:
                        self.planets.append(best_planet)
                        best_planet.statistics["population"] = 2
                        planet.statistics["population"] = planet.statistics["population"] - 2


            for stat in planet.statistics:
                if stat != "population":
                    planet.statistics[stat] = self.production[stat] * planet.statistics["population"]

            self.money += planet.statistics["revenue"]