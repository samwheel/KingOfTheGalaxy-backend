from src.technology import Technology

def make_tech_tree() -> list[Technology]:
    tech_tree: list[Technology] = []

    starting_tech = Technology(
        name="Type I Civilization",
        description="A civilization that has harnessed the energy resources of its home planet. Allows for research and development of new technologies.",
        effect=lambda empire: None
    )

    tech_tree.append(starting_tech)

    fusion_generation = Technology(
        name="Fusion Power Generation",
        description="Harness the power of nuclear fusion to generate energy. Increases GDP production. Requires Type I Civilization.",
        effect=lambda empire: empire.increase_GDP_production(3),
        prerequisites=[starting_tech]
    )

    tech_tree.append(fusion_generation)

    return tech_tree