from depends import get_db
import re
from bson import ObjectId

PROCESSING_BATCH = 100
SKIP = 0
db = get_db()

spot = db.singletons.find_one({"_id": "spot_prices"})


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


while True:
    data = list(db.products.find({}).skip(SKIP).limit(PROCESSING_BATCH))
    if len(data) == 0:
        break

    for p in data:
        is_oz = p['metal_size_unit'].endswith("oz")
        is_g = p['metal_size_unit'].endswith("g")
        is_kg = p['metal_size_unit'].endswith("kg")

        if is_oz:
            num = p['metal_size_unit'].split("oz")[0]
        elif is_g:
            num = p['metal_size_unit'].split("g")[0]
        elif is_kg:
            num = p['metal_size_unit'].split("kg")[0]

        num = convert_to_float(num)

        cost_per_unit = round(p['price'] / num, 2)
        price_over_spot = None

        if p['metal_type'] == "gold" and is_oz:
            price_over_spot = round((cost_per_unit - spot['gold_oz']) * num, 2)
        elif p['metal_type'] == "gold" and is_g:
            price_over_spot = round((cost_per_unit - spot['gold_g']) * num, 2)
        elif p['metal_type'] == "gold" and is_kg:
            price_over_spot = round((cost_per_unit - spot['gold_kg']) * num, 2)

        elif p['metal_type'] == "silver" and is_oz:
            price_over_spot = round((cost_per_unit - spot['silver_oz']) * num, 2)
        elif p['metal_type'] == "silver" and is_kg:
            price_over_spot = round((cost_per_unit - spot['silver_kg']) * num, 2)
        elif p['metal_type'] == "silver" and is_g:
            price_over_spot = round((cost_per_unit - spot['silver_g']) * num, 2)
        price_over_spot_percent = round((price_over_spot / cost_per_unit) * 100, 2)
        #TODO batch process

        db.products.update_many({"_id": ObjectId(p['_id'])}, {"$set": {"cost_per_unit": cost_per_unit,
                                                                          "price_over_spot": price_over_spot,
                                                                       "price_over_spot_percent": price_over_spot_percent}})


    SKIP += PROCESSING_BATCH


