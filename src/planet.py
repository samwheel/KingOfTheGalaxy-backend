planet_environments = ["Terran", "Ocean", "Swamp", "Toxic", "Volcanic", "Radiated", "Barren", "Tundra", "Desert", "Asteroid", "Gas Giant"]

class Planet:
    def __init__(self, name:str, environment: str = "Terran"):
        self.name: str = name
        self.environment: str = environment.title()
        if self.environment not in planet_environments:
            raise ValueError(f"Invalid environment '{self.environment}' for planet '{self.name}'. Must be one of {planet_environments}.")
        self.statistics: dict[str, float] = {"population": 0, "revenue": 0, "research": 0, "defense": 0, "detection_range": 0}

    def __str__(self) -> str:
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "environment": self.environment,
            "statistics": self.statistics
        }