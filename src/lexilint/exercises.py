"""Built-in practice challenges for lexilint.

Each challenge ships deliberately flawed code plus a reference solution. The
flawed source must trigger the listed target rules; the reference solution must
lint clean AND satisfy the behavior cases, so "fixing the lint" can never be
done by deleting functionality.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BehaviorCase:
    call: str  # expression evaluated in the solution's module namespace
    expected: str  # exact repr of the printed/returned value


@dataclass(frozen=True)
class Challenge:
    challenge_id: str
    title: str
    brief: str
    target_rules: tuple[str, ...]
    flawed: str
    reference: str
    behavior: tuple[BehaviorCase, ...]


CHALLENGES: list[Challenge] = [
    Challenge(
        challenge_id="C1",
        title="The Chatty Ingestor",
        brief=(
            "This loader works, but it talks directly to stdout and hides real "
            "errors. Make it silent, catch only what it can handle, and stop "
            "building output with string concatenation."
        ),
        target_rules=("LL201", "LL202", "LL206"),
        flawed='''\
def load_numbers(values):
    total = 0
    seen = []
    for value in values:
        try:
            seen.append(int(value))
        except:
            print("skipping " + str(value))
    print("total is " + str(total))
    return seen
''',
        reference='''\
def load_numbers(values):
    seen = []
    for value in values:
        try:
            seen.append(int(value))
        except ValueError:
            continue
    return seen
''',
        behavior=(
            BehaviorCase('load_numbers(["3", "x", "5"])', "[3, 5]"),
        ),
    ),
    Challenge(
        challenge_id="C2",
        title="The Shared Basket",
        brief=(
            "Customers keep finding items from previous baskets. Find the state "
            "leak, and while you are in there, compare to None the right way."
        ),
        target_rules=("LL203", "LL204"),
        flawed='''\
def new_basket(items=[], coupon=None):
    if coupon == None:
        coupon = "none"
    items.append(coupon)
    return items
''',
        reference='''\
def new_basket(items=None, coupon=None):
    if items is None:
        items = []
    if coupon is None:
        coupon = "none"
    items = [*items, coupon]
    return items
''',
        behavior=(
            BehaviorCase('new_basket()', "['none']"),
            BehaviorCase('new_basket()', "['none']"),
            BehaviorCase('new_basket(["tea"], "GIFT")', "['tea', 'GIFT']"),
        ),
    ),
    Challenge(
        challenge_id="C3",
        title="The Broken Aggregator",
        brief=(
            "Someone renamed the input to 'sum' and marked what they did not "
            "understand with a TODO. Restore clarity and finish the work."
        ),
        target_rules=("LL205", "LL102", "LL206"),
        flawed='''\
sum = 0

# TODO: handle empty input
def average(values):
    total = 0
    for value in values:
        total = total + value
    result = "avg: " + str(total / len(values))
    return result
''',
        reference='''\
def average(values):
    if not values:
        return "avg: n/a"
    total = 0
    for value in values:
        total = total + value
    return f"avg: {total / len(values)}"
''',
        behavior=(
            BehaviorCase('average([2, 4, 6])', "'avg: 4.0'"),
            BehaviorCase('average([])', "'avg: n/a'"),
        ),
    ),
    Challenge(
        challenge_id="C4",
        title="The Wild Formatter",
        brief=(
            "This reporter ignores line discipline, leaks its scratchpad "
            "markers, and formats with concatenation. Tidy it end to end."
        ),
        target_rules=("LL101", "LL102", "LL206"),
        flawed='''\
def format_rows(rows):
    # TODO: escaping
    out = ""
    for row in rows:
        out = out + row[0] + "=" + row[1] + (";" + row[2] if len(row) > 2 else "") + (";" + row[3] if len(row) > 3 else "")
    return out
''',
        reference='''\
def format_rows(rows):
    rendered = []
    for row in rows:
        head = "=".join(row[:2])
        tail = row[2:]
        if tail:
            rendered.append(";".join([head, *tail]))
        else:
            rendered.append(head)
    return ";".join(rendered)
''',
        behavior=(
            BehaviorCase(
                'format_rows([("a", "1"), ("b", "2", "x")])',
                "'a=1;b=2;x'",
            ),
        ),
    ),
]


def get_challenge(challenge_id: str) -> Challenge:
    for challenge in CHALLENGES:
        if challenge.challenge_id == challenge_id:
            return challenge
    raise KeyError(f"unknown challenge: {challenge_id}")
