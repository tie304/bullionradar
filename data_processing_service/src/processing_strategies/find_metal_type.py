from src.processing_strategies.util import count_indexes

METAL_FORMS = ['gold', 'silver']

def find_metal_type(title, description):
    instances = {}

    title = title.lower()
    if description:
        description = description.lower()
    else:
        description = " "

    for form in METAL_FORMS:
        count = count_indexes(form, title + description)
        instances[form] = count

    if instances['gold'] > instances['silver'] and instances['gold'] > instances['platinum']:
        return "gold"
    elif instances['silver'] > instances['gold'] and instances['silver'] > instances['platinum']:
        return "silver"

    raise ValueError("unknown metal form")