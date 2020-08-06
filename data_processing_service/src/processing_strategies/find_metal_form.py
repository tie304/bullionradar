from src.processing_strategies.util import count_indexes

FORM_TYPES = ["bar", "coin", "round"]


def find_metal_form(title=" ", description="?????"):
    instances = {}

    title = title.lower()
    if description:
        description = description.lower()
    else:
        description = " "

    for form in FORM_TYPES:
        count = count_indexes(form, title + description)
        instances[form] = count

    if instances['coin'] > instances['bar'] and instances['coin'] > instances['round']:
        return "coin"
    elif instances['bar'] > instances['coin'] and instances['bar'] > instances['round']:
        return "bar"
    elif instances['round'] > instances['coin'] and instances['round'] > instances['bar']:
        return "round"

    raise ValueError("unknown metal form")
