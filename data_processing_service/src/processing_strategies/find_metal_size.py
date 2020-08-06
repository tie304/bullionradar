import sys
import re

METAL_SIZES_ABBV = [" g ", " oz ", " kg "]
METAL_SIZES_FULL_SINGLE = ["gram", "ounce", "kilogram"]
METAL_SIZES_FULL_PLURAL = ["grams", "ounces", "kilograms"]

def count_indexes(word, string):
    matches = re.finditer(word, string)
    return len([match.start() for match in matches])


def get_indexes(word, string):
    matches = re.finditer(word, string)
    return [match.start() for match in matches]


def find_number(indexes: list, search_string):
    str_numbers = []
    for index in indexes:
        num_str = ""
        for i in range(index - 1, -1, -1):
            if search_string[i].isdigit() or search_string[i] in ["/","."]:
                num_str += search_string[i]
            if search_string[i].isspace() and i != index -1 or i == 0 and len(search_string) > 0:
                str_numbers.append(num_str[::-1])
                break
    if not str_numbers or not str_numbers[0].isdigit():
        raise ValueError("no numbers found inside string")
    return str_numbers[0]




def find_metal_size(title, description):
    if description:
        description = description.lower()
    else:
        description = " "

    title = title.lower()
    combine = title
    found_dict = {"g": 0, "oz":0, "kg": 0}
    for type,  abrv, single, plural in zip(["g", "oz", "kg"],METAL_SIZES_ABBV, METAL_SIZES_FULL_SINGLE, METAL_SIZES_FULL_PLURAL):

        total_index = 0

        total_index += count_indexes(abrv, combine)
        total_index += count_indexes(single, combine)
        total_index += count_indexes(plural, combine)

        found_dict[type] += total_index

    most_used_metric = max(found_dict, key=found_dict.get)

    indexes_of_most_used = get_indexes(most_used_metric, combine)

    number = find_number(indexes_of_most_used, combine)

    return number + most_used_metric





