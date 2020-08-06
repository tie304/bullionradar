import re

def count_indexes(word, string):
    matches = re.finditer(word, string)
    return len([match.start() for match in matches])