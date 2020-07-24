import csv
import requests
import validators
from bs4 import BeautifulSoup

csv_headers = ['site', 'name', 'url', 'description', 'in_stock_selector', 'in_stock_selector_type', 'price_selector', 'size', 'type']
optional_columns = ['description']
valid_selectors = ["if_exists", "not_exists"]
valid_metal_types = ["gold", "silver"]


def check_valid_selector_type(selector: str):
    if selector in valid_selectors:
        return True
    return False


def check_valid_metal_type(type: str):
    if type in valid_metal_types:
        return True
    return False


accepted_types = {
    "site": {
        "type": str,
    },
    "name": {
        "type": str,
    },
    "url": {
        "type": str,
        "validation": validators.url
    },
    "description": {
        "type": str
    },
    "in_stock_selector": {
        "type": str,
    },
    "in_stock_selector_type": {
        "type": str,
        "validation": check_valid_selector_type
    },
    "price_selector": {
        "type": str,
    },
    "size": {
        "type": str
    },
    "type": {
        "type": str,
        "validation": check_valid_metal_type
    }
}


def parse_price_to_float(price: str) -> float:
    cleaned_str = ""
    for char in price:
        if char == "." or char.isdigit():
            cleaned_str += char
    return float(cleaned_str)



def validate_csv(csv_str: str) -> None:
    """

    Validates csv before putting into database
    Args:
        csv_str (str): string verison of cev
    """
    csv_reader = csv.reader(csv_str.splitlines(), delimiter=',')
    row_count = 0
    for row in csv_reader:
        col_idx = 0
        if row_count == 0:
            assert row == csv_headers, "incorrect csv row headers provided"
        else:
            for col in row:
                optional = csv_headers[col_idx] in optional_columns
                if not optional:
                    assert col, f"column missing {row_count + 1}, {col_idx + 1}"
                    # calls validation function with col
                    if accepted_types[csv_headers[col_idx]].get("validation"):
                        assert accepted_types[csv_headers[col_idx]].get("validation")(col), f"failed validation function {csv_headers[col_idx]} {row_count + 1}, {col_idx + 1}"
                    assert isinstance(col, accepted_types[csv_headers[col_idx]].get("type")), f"failed to validate type {csv_headers[col_idx]} {row_count + 1}, {col_idx + 1}"
                elif optional and col:
                    if accepted_types[csv_headers[col_idx]].get("validation"):
                        assert accepted_types[csv_headers[col_idx]].get("validation")(col), f"failed validation function {csv_headers[col_idx]} {row_count + 1}, {col_idx + 1}"
                    assert isinstance(col, accepted_types[csv_headers[col_idx]].get("type")), f"failed to validate type {csv_headers[col_idx]} {row_count + 1}, {col_idx + 1}"

                col_idx += 1
        row_count += 1


def validate_requests(csv_str: str) -> None:
    csv_reader = csv.reader(csv_str.splitlines(), delimiter=',')
    row_idx = 0
    for row in csv_reader:
        if row_idx > 0:
            res = requests.get(row[2])
            assert res.ok, f"bad response for url: {row[2]}"
            soup = BeautifulSoup(res.text, features="html.parser")
            price_element = soup.select(row[6])
            assert price_element, f"could not find price element from {row[2]}"
            price_element = price_element[0].text.strip()
            assert isinstance(parse_price_to_float(price_element), float)
        row_idx +=1

