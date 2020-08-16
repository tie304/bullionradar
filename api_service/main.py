from fastapi import FastAPI, Query, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from api.models.search import ProductSearch, Metals, PriceSort
from api.utils import object_id_converter
from depends import get_db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="frontend/templates")

search_schema = { #TODO make dynamic
    "metal_type": ["gold", "silver"],
    "bullion_size": ["1g", "2g", "2.5g", "1oz", "5oz", "10oz"],
    "bullion_form": ["coin", "round", "bar"]
}

@app.get("/api/products")
def read_item(request: Request,
              gold: Optional[bool] = Query(False),
              silver: Optional[bool] = Query(False),
              bullion_size : Optional[str] = Query(None),
              bullion_form: Optional[str] = Query(None),
              skip: int = Query(0)) -> List[dict]:
    db = get_db()

    query = {"stock": True}

    query["price_over_spot_percent"] = {"$exists": True}
    query["error"] =  {"$ne": True}

    if gold or silver:
        metal_types = []
        if gold:
            metal_types.append(Metals.gold)
        if silver:
            metal_types.append(Metals.silver)
        query['metal_type'] = {"$in": metal_types}

    if bullion_size:
        query['metal_size_unit'] = bullion_size

    if bullion_form:
        query['metal_form'] = bullion_form

    cursor = db.products.find(query).sort("price_over_spot_percent", 1).limit(50).skip(skip)
    count = cursor.count()
    products = object_id_converter(list(cursor))
    spot_prices = db.singletons.find_one({"_id": "spot_prices"})
    next_skip = skip + 50
    if skip - 50 < 0 :
        prev_skip = 0
    else:
        prev_skip = skip - 50
    return templates.TemplateResponse("pages/search.html", {"request": request,
                                                      "search": {
                                                          "count": count,
                                                          "pagination_count": skip + len(products),
                                                          "next_skip": next_skip,
                                                          "prev_skip": prev_skip,
                                                          "search_schema": search_schema,
                                                          "gold": gold,
                                                          "silver": silver,
                                                          "bullion_size": bullion_size,
                                                          "bullion_form": bullion_form
                                                      },
                                                     "products": products,
                                                     "gold_oz": spot_prices.get('gold_oz'),
                                                     "gold_g": spot_prices.get("gold_g"),
                                                     "gold_kg": spot_prices.get("gold_kg"),
                                                     "silver_oz": spot_prices.get("silver_oz"),
                                                     "silver_g": spot_prices.get("silver_g"),
                                                     "silver_kg": spot_prices.get("silver_kg")})



@app.get("/")
async def read_item(request: Request):
    db = get_db()
    spot_prices = db.singletons.find_one({"_id": "spot_prices"})
    return templates.TemplateResponse("pages/landing.html", {"request": request,
                                                     "search": {
                                                         "search_schema": search_schema,
                                                     },
                                                     "gold_oz": spot_prices.get('gold_oz'),
                                                     "gold_g": spot_prices.get("gold_g"),
                                                     "gold_kg": spot_prices.get("gold_kg"),
                                                     "silver_oz": spot_prices.get("silver_oz"),
                                                     "silver_g": spot_prices.get("silver_g"),
                                                     "silver_kg": spot_prices.get("silver_kg")})
