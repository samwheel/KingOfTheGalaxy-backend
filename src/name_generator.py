from random import Random

def generate_name_list(amount: int = 1, random_number_generator: Random | None = None) -> list[str]:
    randomizer = random_number_generator if random_number_generator else Random()
    with open("src/star_names.txt") as file:
        name_list = file.readlines()
    randomizer.shuffle(name_list)
    return name_list[:amount]


def generate_prefix_list(amount: int = 1, random_number_generator: Random | None = None) -> list[str]:
    randomizer = random_number_generator if random_number_generator else Random()
    prefixes = "αβεγλμηξδνθω"
    prefix_list = [prefix for prefix in prefixes]
    randomizer.shuffle(prefix_list)
    return prefix_list[:amount]

