import csv
import datetime
from depends import get_db

csv_headers = ['site', 'name', 'url', 'description', 'in_stock_selector', 'in_stock_selector_type', 'price_selector', 'size', 'type']

def create_products(csv_str: str) -> None:
    db = get_db()
    csv_reader = csv.reader(csv_str.splitlines(), delimiter=',')
    row_idx = 0
    queries = []
    for row in csv_reader:
        if row_idx > 0:
            query = {}
            query['site'] = row[0].strip("/") # for standardization
            query['name'] = row[1]
            query['url'] = row[2].strip("/") # for standardization
            query['size'] = row[7]
            query['type'] = row[8]
            query['description'] = row[3]
            query['updated'] = datetime.datetime.utcnow()
            queries.append(query)
        row_idx +=1
    for q in queries:
        db.products.update_one({"url": q['url']}, {"$set": q}, upsert=True)


def create_scraping_jobs(csv_str: str) -> None:
    db = get_db()
    csv_reader = csv.reader(csv_str.splitlines(), delimiter=',')
    row_idx = 0
    queries = []
    for row in csv_reader:
        if row_idx > 0:
            query = {}
            query['type'] = "product"
            query['parent'] = row[0].strip("/")
            query['url'] = row[2].strip("/")  # for standardization
            query['scraping_metadata'] = {
                "in_stock": {
                    "selector": row[4],
                },
                "price": {
                    "selector": row[6],
                    "value_extract": True,
                    "value_type": "float"
                }
            }
            query['scraping_metadata']['in_stock'][row[5]] = True
            query['updated'] = datetime.datetime.utcnow()
            queries.append(query)
        row_idx += 1
    for q in queries:
        db.scraping_jobs.update_one({"url": q['url']}, {"$set": q}, upsert=True)