from typing import Callable


class Technology:
    def __init__(self, name: str, description: str, effect: Callable, prerequisites: list[Technology] | None = None) -> None:
        self.name: str = name
        self.description: str = description
        self.effect: Callable = effect
        self.prerequisites: list[Technology] = prerequisites if prerequisites is not None else []
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "prerequisites": [tech.name for tech in self.prerequisites],
        }