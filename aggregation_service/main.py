from depends import get_db
import re
from bson import ObjectId
from src.calculate_value import calculate_value

PROCESSING_BATCH = 100
SKIP = 0
db = get_db()

spot = db.singletons.find_one({"_id": "spot_prices"})

while True:
    data = list(db.products.find({"error": {"$ne": True}}).skip(SKIP).limit(PROCESSING_BATCH))
    if len(data) == 0:
        break

    for p in data:
        price_over_spot_percent, price_over_spot, cost_per_unit = calculate_value(p, spot)

        db.products.update_many({"_id": ObjectId(p['_id'])}, {"$set": {"cost_per_unit": cost_per_unit,
                                                                          "price_over_spot": price_over_spot,
                                                                       "price_over_spot_percent": price_over_spot_percent}})


    SKIP += PROCESSING_BATCH


