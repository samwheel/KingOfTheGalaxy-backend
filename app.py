#!/Users/samwise/Projects/Python/KingOfTheGalaxy/.venv/bin/python

from flask import Flask, jsonify, request
from flask_cors import CORS
from rich import print

from src.standard_game_factory import StandardGameFactory
from src.empire import Empire
from src.ship import SHIP_MODELS, Ship, StarLocation

game_factory = StandardGameFactory()
current_game = game_factory.create_game()

player_empire = Empire("Terran Imperium", "cyan")
homeplanet = game_factory.create_homeplanet(current_game)
homestar = next(star for star in current_game.starmap if homeplanet in star.planets)
homeplanet.statistics["population"] = 1
for stat in homeplanet.statistics:
    if stat != "population":
        homeplanet.statistics[stat] = player_empire.production[stat] * homeplanet.statistics["population"]
player_empire.planets.append(homeplanet)
current_game.ships.append(Ship("Pioneer", 2, 100, 1, 10, 5, StarLocation(homestar), detection_range=5, owner_name=player_empire.name))

current_game.empires = [player_empire]
current_game.update_detectable_regions()

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith(("/ships", "/starmap", "/empires", "/tech_tree", "/turn")):
            return jsonify({"error": "API route not found"}), 404
        return error

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to the King of the Galaxy API!"})

    @app.route("/starmap")
    def get_starmap():
        return jsonify([star.to_dict() for star in current_game.starmap])
    
    @app.route("/starmap/<star_name>")
    def get_star(star_name: str):
        star = next((s for s in current_game.starmap if s.name == star_name), None)
        if star:
            star_dict = star.to_dict()
            star_dict["planets"] = [planet.to_dict() for planet in star.planets]
            return jsonify(star_dict)
        return jsonify({"error": "Star not found"}), 404

    @app.route("/tech_tree")
    def get_tech_tree():
        return jsonify([tech.to_dict() for tech in current_game.tech_tree])

    @app.route("/empires")
    def get_empires():
        return jsonify([empire.to_dict() for empire in current_game.empires])

    @app.route("/empires/<empire_name>")
    def get_empire(empire_name: str):
        empire = next((e for e in current_game.empires if e.name == empire_name), None)
        if empire:
            return jsonify(empire.to_dict())
        return jsonify({"error": "Empire not found"}), 404

    @app.route("/ships")
    def get_ships():
        return jsonify([ship.to_dict() for ship in current_game.ships])

    @app.route("/shipyard")
    def get_shipyard():
        return jsonify([
            {"model_name": model_name, **specification}
            for model_name, specification in SHIP_MODELS.items()
        ])

    @app.route("/empires/<empire_name>/ships", methods=["POST"])
    def purchase_ship(empire_name: str):
        empire = next((item for item in current_game.empires if item.name == empire_name), None)
        if empire is None:
            return jsonify({"error": "Empire not found"}), 404

        payload = request.get_json(silent=True) or {}
        model_name = payload.get("model_name")
        planet_name = payload.get("planet")
        if not isinstance(model_name, str) or not isinstance(planet_name, str):
            return jsonify({"error": "Ship model and construction planet are required"}), 400
        specification = SHIP_MODELS.get(model_name)
        if specification is None:
            return jsonify({"error": "Unknown ship model"}), 400

        planet = next((item for item in empire.planets if item.name == planet_name), None)
        if planet is None:
            return jsonify({"error": "Planet is not controlled by this empire"}), 400
        if empire.money < specification["cost"]:
            return jsonify({"error": "Insufficient funds"}), 400

        star = next((item for item in current_game.starmap if planet in item.planets), None)
        if star is None:
            return jsonify({"error": "Planet is not on the starmap"}), 400

        empire.money -= specification["cost"]
        ship_number = sum(ship.model_name.startswith(model_name) for ship in current_game.ships) + 1
        ship = Ship(
            f"{model_name}-{ship_number}",
            specification["speed"],
            specification["fuel_capacity"],
            specification["fuel_consumption"],
            specification["armor"],
            specification["weapon_power"],
            StarLocation(star),
            detection_range=specification["detection_range"],
            owner_name=empire.name,
        )
        current_game.ships.append(ship)
        current_game.update_detectable_regions()
        return jsonify({"ship": ship.to_dict(), "empire": empire.to_dict()}), 201

    @app.route("/ships/<ship_name>/move", methods=["POST"])
    def move_ship(ship_name: str):
        ship = next((item for item in current_game.ships if item.model_name == ship_name), None)
        if ship is None:
            return jsonify({"error": "Ship not found"}), 404

        destination_name = request.json.get("destination") if request.is_json else None
        destination = next((star for star in current_game.starmap if star.name == destination_name), None)
        if destination is None:
            return jsonify({"error": "Destination star not found"}), 400

        if not isinstance(ship.location, StarLocation):
            return jsonify({"error": "A ship already traveling on a star lane cannot change course"}), 400

        path = current_game.shortest_path(ship.location.star, destination)
        if path is None:
            return jsonify({"error": "No star lane route to destination"}), 400

        try:
            ship.set_course(path)
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

        return jsonify(ship.to_dict())

    @app.route("/turn_update", methods=["POST"])
    def turn_update():
        current_game.turn_update()
        return jsonify({"message": "Turn updated successfully"})

    @app.route("/turn")
    def get_turn():
        return jsonify({"turn": current_game.turn})

    return app

print(f"[bold green]Game generated with {len(current_game.starmap)} stars, {len(current_game.tech_tree)} technologies, and {len(current_game.empires)} empire{len(current_game.empires) != 1 and 's' or ''}.[/bold green]")

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)