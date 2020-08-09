

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac


def calculate_value(p, spot):
    is_oz = p['metal_size_unit'].endswith("oz")
    if p['metal_size_unit'].endswith("g") and not p['metal_size_unit'].endswith("kg"):
        is_g = True
    else:
        is_g = False
    is_kg = p['metal_size_unit'].endswith("kg")

    if is_oz:
        num = p['metal_size_unit'].split("oz")[0]
    elif is_kg:
        num = p['metal_size_unit'].split("kg")[0]
    elif is_g:
        num = p['metal_size_unit'].split("g")[0]


    num = convert_to_float(num)

    cost_per_unit = round(p['price'] / num, 2)
    price_over_spot = None

    if p['metal_type'] == "gold" and is_oz:
        price_over_spot = round((cost_per_unit - spot['gold_oz']), 3)
        price_over_spot_percent = round((price_over_spot / spot['gold_oz']), 3)
    elif p['metal_type'] == "gold" and is_g:
        price_over_spot = round((cost_per_unit - spot['gold_g']), 3)
        price_over_spot_percent = round((price_over_spot / spot['gold_g']), 3)
    elif p['metal_type'] == "gold" and is_kg:
        price_over_spot = round((cost_per_unit - spot['gold_kg']), 3)
        price_over_spot_percent = round((price_over_spot / spot['gold_kg']), 3)

    elif p['metal_type'] == "silver" and is_oz:
        price_over_spot = round((cost_per_unit - spot['silver_oz']), 3)
        price_over_spot_percent = round((price_over_spot / spot['silver_oz']), 3)
    elif p['metal_type'] == "silver" and is_kg:
        price_over_spot = round((cost_per_unit - spot['silver_kg']), 3)
        price_over_spot_percent = round((price_over_spot / spot['silver_kg']), 3)
    elif p['metal_type'] == "silver" and is_g:
        price_over_spot = round((cost_per_unit - spot['silver_g']), 3)
        price_over_spot_percent = round((price_over_spot / spot['silver_g']), 3)

    price_over_spot_percent = round(price_over_spot_percent * 100, 3)

    return price_over_spot_percent, price_over_spot, cost_per_unit