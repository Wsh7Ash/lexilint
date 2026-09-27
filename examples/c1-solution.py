"""Reference solution for challenge C1 — grade it with:

    lexilint grade C1 examples/c1-solution.py
"""


def load_numbers(values):
    seen = []
    for value in values:
        try:
            seen.append(int(value))
        except ValueError:
            continue
    return seen
