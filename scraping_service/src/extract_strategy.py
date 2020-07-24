from bs4 import BeautifulSoup
from bson import ObjectId


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

        if data.get('if_exists') and element:
            extracted_data[data_point] = True
        elif data.get('not_exists') and not element:
            extracted_data[data_point] = True
        elif data.get('if_exists') and not element:
            extracted_data[data_point] = False
        elif data.get('not_exists') and element:
            extracted_data[data_point] = False
        elif data.get('value_extract') and not element:
            raise ValueError("element to extract value not found")
        elif data.get('value_extract') and element:
            if data.get('value_type') == "float": # extracts float values
                float_extract = element[0].text.strip()
                float_value = parse_price_to_float(float_extract)
                extracted_data[data_point] = float_value
    return extracted_data




def extract_spot_from_html(data: str, spot_singleton: dict, type: str):
    soup = BeautifulSoup(data, features="html.parser")
    if type == "gold":
        g = parse_price_to_float(soup.select(spot_singleton['gold']['selectors']['g'])[0].text.strip())
        oz = parse_price_to_float(soup.select(spot_singleton['gold']['selectors']['oz'])[0].text.strip())
        kg = parse_price_to_float(soup.select(spot_singleton['gold']['selectors']['kg'])[0].text.strip())
        return g, oz, kg

    if type == "silver":
        g = parse_price_to_float(soup.select(spot_singleton['silver']['selectors']['g'])[0].text.strip())
        oz = parse_price_to_float(soup.select(spot_singleton['silver']['selectors']['oz'])[0].text.strip())
        kg = parse_price_to_float(soup.select(spot_singleton['silver']['selectors']['kg'])[0].text.strip())
        return g, oz, kg








