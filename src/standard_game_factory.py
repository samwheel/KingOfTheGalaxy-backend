import math

from src.game import Game
from src.tech_tree import make_tech_tree
from src.star import Star
from src.planet import Planet, planet_environments
from src.name_generator import generate_name_list, generate_prefix_list
from src.roman import int_to_roman

from random import Random
from rich import print
class StandardGameFactory:
    def __init__(self, seed: int | None = None):
        self.random = Random(seed)

    def _has_star_lane_connection(self, star: Star, other_star: Star) -> bool:
        return other_star in star.star_lane_connections or star in other_star.star_lane_connections

    def _calculate_distance(self, star: Star, other_star: Star) -> float:
        return ((star.coordinates[0] - other_star.coordinates[0]) ** 2 + (star.coordinates[1] - other_star.coordinates[1]) ** 2) ** 0.5

    def _is_closely_connected(self, star: Star, other_star: Star, starlane_jumps: int = 2, max_distance: float = float("inf")) -> bool:
        if star is other_star:
            return True

        if self._has_star_lane_connection(star, other_star):
            return True

        if ((star.coordinates[0] - other_star.coordinates[0]) ** 2 + (star.coordinates[1] - other_star.coordinates[1]) ** 2) ** 0.5 > max_distance:
            return False

        visited_stars = set()
        stars_to_visit = [star]

        for _ in range(starlane_jumps):
            next_stars_to_visit = []
            for current_star in stars_to_visit:
                if current_star in visited_stars:
                    continue
                visited_stars.add(current_star)
                next_stars_to_visit.extend(current_star.star_lane_connections)

            stars_to_visit = next_stars_to_visit

        return other_star in visited_stars

    def _connect_stars(self, star: Star, other_star: Star) -> bool:
        if star is other_star or self._has_star_lane_connection(star, other_star):
            return False

        star.star_lane_connections.append(other_star)
        other_star.star_lane_connections.append(star)
        return True

    def _get_closest_star_pair(self, stars: list[Star], max_distance: float = float("inf")) -> tuple[Star | None, Star | None]:
        closest_star_pair: tuple[Star | None, Star | None] = (None, None)
        closest_distance: float = float("inf")

        for index, star in enumerate(stars):
            if len(star.star_lane_connections) >= 2:
                continue
            for other_star in stars[index + 1 :]:
                if self._has_star_lane_connection(star, other_star):
                    continue
                if self._is_closely_connected(star, other_star, starlane_jumps=3, max_distance=30):
                    continue

                distance = self._calculate_distance(star, other_star)
                if distance > 30:
                    if len(other_star.star_lane_connections) >= 2:
                        continue
                else:
                    if len(other_star.star_lane_connections) >= 3:
                        continue
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_star_pair = (star, other_star)
        if closest_distance > max_distance:
            print(f"[bold yellow]Skipping connection between {closest_star_pair[0]} and {closest_star_pair[1]} due to distance {closest_distance:.2f} exceeding max_distance {max_distance}[/bold yellow]")
            return (None, None)
        
        return closest_star_pair

    def _get_closest_star(self, star: Star, stars: list[Star]) -> Star | None:
        closest_star: Star | None = None
        closest_distance: float = float("inf")

        for other_star in stars:
            if other_star == star:
                continue

            distance = ((star.coordinates[0] - other_star.coordinates[0]) ** 2 + (star.coordinates[1] - other_star.coordinates[1]) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_star = other_star

        return closest_star

    def create_game(self) -> Game:
        starmap = []
        star_names = set()
        cluster_names = generate_name_list(self.random.randint(4, 20), self.random)
        current_coordinates = (0, 0)
        for cluster_name in cluster_names:
            prefixes = generate_prefix_list(self.random.randint(1, 10), self.random)
            for prefix in prefixes:
                star_name = f"{prefix} {cluster_name}"
                if star_name in star_names:
                    continue

                x_direction = self.random.randint(0, 1) * 2 - 1
                y_direction = self.random.randint(0, 1) * 2 - 1
                x_increase = x_direction * self.random.randint(20, 40)
                y_increase = y_direction * self.random.randint(20, 40)
                current_coordinates = (current_coordinates[0] + x_increase, current_coordinates[1] + y_increase)

                planets = [Planet(f"{prefix} {cluster_name} {int_to_roman(index + 1)}", self.random.choice(planet_environments)) for index in range(self.random.randint(0, 5))]
                new_star = Star(star_name, current_coordinates, planets)

                closest_star = self._get_closest_star(new_star, starmap)
                if closest_star:
                    self._connect_stars(new_star, closest_star)
                starmap.append(new_star)
                star_names.add(star_name)

        # Create additional connections between stars to ensure a more interconnected starmap
        for _ in range(math.floor(len(starmap) * 0.3)):
            star_pair = self._get_closest_star_pair(starmap, max_distance=90)
            if star_pair[0] and star_pair[1]:
                self._connect_stars(star_pair[0], star_pair[1])
            else:
                break  # No more valid star pairs to connect

        return Game(starmap, make_tech_tree())

    def create_homeplanet(self, game: Game) -> Planet:
        homestar = None
        while not homestar:
            star = self.random.choice(game.starmap)
            if star.planets:
                homestar = star

        return self.random.choice(homestar.planets)