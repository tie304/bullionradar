from bs4 import BeautifulSoup
from bson import ObjectId
import sys


def parse_price_to_float(price: str) -> float:
    cleaned_str = ""
    for char in price:
        if char == "." or char.isdigit():
            cleaned_str += char
    return float(cleaned_str)


def extract_data_from_html(data: str, job: dict) -> dict:
    soup = BeautifulSoup(data, features="html.parser")
    extracted_data = {}

    for data_point, data in job['scraping_metadata'].items():
        element = soup.select(data['selector'])
        selector_strategy = data['selector_strategy']
        selector_type = data['selector_type']

        if selector_strategy == 'if_exists' and element:
            extracted_data[data_point] = True
        elif selector_strategy == 'not_exists' and not element:
            extracted_data[data_point] = True
        elif selector_strategy == 'if_exists' and not element:
            extracted_data[data_point] = False
        elif selector_strategy == 'not_exists' and element:
            extracted_data[data_point] = False
        elif selector_strategy == 'should_exist' and not element:
            raise ValueError("element to extract value not found")
        elif selector_strategy == 'should_exist' and element:
            if selector_type == "float": # extracts float values
                float_extract = element[0].text.strip()
                float_value = parse_price_to_float(float_extract)
                extracted_data[data_point] = float_value
    return extracted_data






