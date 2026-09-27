"""A deliberately sloppy module used to demonstrate `lexilint lint`."""


def describe(items=[]):
    # TODO: pick a better label
    if items == None:
        items = []
    try:
        first = items[0]
    except:
        first = "nothing"
    return "items: " + str(len(items)) + " first: " + first
