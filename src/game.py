from src.empire import Empire
from src.star import Star
from src.ship import Ship
from src.technology import Technology
from collections import deque

class Game:
    def __init__(self, starmap: list[Star], tech_tree: list[Technology], empires: list[Empire] | None = None, ships: list[Ship] | None = None):
        self.starmap: list[Star] = starmap
        self.tech_tree: list[Technology] = tech_tree
        self.empires: list[Empire] = empires if empires is not None else []
        self.ships: list[Ship] = ships if ships is not None else []
        self.turn: int = 0

    def turn_update(self):
        self.turn += 1
        for ship in self.ships:
            ship.advance()
        for empire in self.empires:
            empire.turn_update(self.starmap)
        self.update_detectable_regions()

    def update_detectable_regions(self):
        for empire in self.empires:
            empire.update_detectable_region(self.starmap, self.ships)

    def shortest_path(self, start: Star, destination: Star) -> list[Star] | None:
        paths = deque([[start]])
        visited = {start}
        while paths:
            path = paths.popleft()
            current = path[-1]
            if current is destination:
                return path
            connections = current.star_lane_connections + [
                star for star in self.starmap
                if current in star.star_lane_connections
                and star not in current.star_lane_connections
            ]
            for connected_star in connections:
                if connected_star in visited:
                    continue
                visited.add(connected_star)
                paths.append(path + [connected_star])
        return None