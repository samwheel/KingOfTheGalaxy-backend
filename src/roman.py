def int_to_roman(value: int) -> str:
    if value <= 0 or value >= 4000:
        raise ValueError("Roman numerals support values from 1 to 3999")

    roman_pairs = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    result = []
    remaining = value
    for integer, numeral in roman_pairs:
        count = remaining // integer
        if count:
            result.append(numeral * count)
            remaining -= integer * count
    return "".join(result)