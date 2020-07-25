import requests
import sys
from depends import get_db

db = get_db()
#TODO add error handling
price_url = "https://data-asg.goldprice.org/dbXRates/USD"
headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1"}

try:
    res = requests.get(price_url, headers=headers)
    troy_ounce_to_gram = 31.103
    troy_ounce_to_kg = 0.0311035
    kg_to_troy_ounce = 32.1507

    gold_price_troy_oz = res.json()['items'][0]['xauPrice']
    silver_price_troy_oz = res.json()['items'][0]['xagPrice']
except Exception as e:
    raise RuntimeError("Failed to retrieve spot price data")


db.singletons.update_one({"_id": "spot_prices"}, {"$set": {"gold_oz": round(gold_price_troy_oz,2) ,
                                                       "gold_g": round(gold_price_troy_oz / troy_ounce_to_gram, 2),
                                                       "gold_kg": round(gold_price_troy_oz * kg_to_troy_ounce, 2),
                                                       "silver_oz": round(silver_price_troy_oz, 2),
                                                       "silver_g": round(silver_price_troy_oz / troy_ounce_to_gram, 2),
                                                       "silver_kg": round(silver_price_troy_oz * kg_to_troy_ounce, 2)}})
