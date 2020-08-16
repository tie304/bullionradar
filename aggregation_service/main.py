from depends import get_db
import re
from bson import ObjectId
from src.calculate_value import calculate_value

PROCESSING_BATCH = 200
SKIP = 0
db = get_db()

spot = db.singletons.find_one({"_id": "spot_prices"})

while True:
    print(SKIP)
    data = list(db.products.find({"error": {"$ne": True}}).skip(SKIP).limit(PROCESSING_BATCH))
    if len(data) == 0:
        break

    for p in data:
        price_over_spot_percent, price_over_spot, cost_per_unit = calculate_value(p, spot)

        # if selling at a loss that should be strange and should be checked out
        if price_over_spot_percent < 0:
            db.products.update_one({"_id": ObjectId(p['_id'])}, {"$set": {"cost_per_unit": cost_per_unit,
                                                                          "price_over_spot": price_over_spot,
                                                                          "price_over_spot_percent": price_over_spot_percent,
                                                                          "error": True}})
            continue # skip loop

        db.products.update_one({"_id": ObjectId(p['_id'])}, {"$set": {"cost_per_unit": cost_per_unit,
                                                                          "price_over_spot": price_over_spot,
                                                                       "price_over_spot_percent": price_over_spot_percent}})


    SKIP += PROCESSING_BATCH


