from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from api.models.search import ProductSearch, Metals, PriceSort
from api.utils import object_id_converter
from depends import get_db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="frontend/templates")

@app.post("/api/products")
def read_item(search: Optional[ProductSearch] = None, skip: int = Query(0)) -> List[dict]:
    db = get_db()
    query = {"stock": False}
    if search:
        if search.metals:
            query['metal_type'] = {"$in": search.metals}
        if search.price:
            if search.price.type == PriceSort.lte:
                query["price"] = {"$lte": search.price.price}
            if search.price.type == PriceSort.gte:
                query["price"] = {"$gte": search.price.price}
        if search.size:
            query['metal_size_unit'] = search.size

    projection = {"scraping_metadata": 0}
    print(query)
    products = object_id_converter(list(db.products.find(query, projection).limit(50).skip(skip)))

    return products



@app.get("/")
async def read_item(request: Request):
    db = get_db()
    spot_prices = db.singletons.find_one({"_id": "spot_prices"})
    #TODO grab with redis
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "gold_oz": spot_prices.get('gold_oz'),
                                                     "gold_g": spot_prices.get("gold_g"),
                                                     "gold_kg": spot_prices.get("gold_kg"),
                                                     "silver_oz": spot_prices.get("silver_oz"),
                                                     "silver_g": spot_prices.get("silver_g"),
                                                     "silver_kg": spot_prices.get("silver_kg")})



