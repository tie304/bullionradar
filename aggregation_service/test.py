from src.calculate_value import calculate_value

spot_prices = {
    "_id": "spot_prices",
    "gold_oz": 2026.96,
    "silver_oz": 28.13,
    "gold_g": 65.17,
    "gold_kg": 65168.18,
    "silver_g": 0.9,
    "silver_kg": 904.26
}

data = [
    {
        "input": {
            "metal_size_unit": "100oz",
            "price": 3324.00,
            "metal_type": "silver"
        },
        "output": {
            "cost_per_unit": 33.24,
            "price_over_spot": 5.11,
            "price_over_spot_percent": 18.2
        }
    },
    {
        "input": {
            "metal_size_unit": "100g",
            "price": 200,
            "metal_type": "silver"
        },
        "output": {
            "cost_per_unit": 2.0,
            "price_over_spot": 1.1,
            "price_over_spot_percent": 122.2
        }
    },
    {
        "input": {
            "metal_size_unit": "100kg",
            "price": 100000,
            "metal_type": "silver"
        },
        "output": {
            "cost_per_unit": 1000,
            "price_over_spot": 95.74,
            "price_over_spot_percent": 10.6
        }
    }
]

for d in data:
    price_over_spot_percent, price_over_spot, cost_per_unit = calculate_value(d['input'], spot_prices)

    print(price_over_spot_percent, price_over_spot, cost_per_unit)

    assert price_over_spot == d['output']['price_over_spot']
    assert cost_per_unit == d['output']['cost_per_unit']
    assert price_over_spot_percent == d['output']['price_over_spot_percent']