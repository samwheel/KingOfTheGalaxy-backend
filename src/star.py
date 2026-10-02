from src.planet import Planet

class Star:
    def __init__(self, name: str, coordinates: tuple, planets: list[Planet] | None = None, star_lane_connections: list[Star] | None = None):
        self.name = name
        self.coordinates = coordinates
        self.planets: list[Planet] = planets if planets is not None else []
        self.star_lane_connections: list[Star] = star_lane_connections if star_lane_connections is not None else []
    
    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "coordinates": self.coordinates,
            "planets": [planet.name for planet in self.planets],
            "planet_details": [planet.to_dict() for planet in self.planets],
            "star_lane_connections": [star.name for star in self.star_lane_connections]
        }