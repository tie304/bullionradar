import bson
import time
import urllib.parse as urlparse
from depends import get_db
from fastapi import FastAPI, File, UploadFile, HTTPException, Query



app = FastAPI()

def clean_hostname(url):
    hostname = urlparse.urlparse(url).hostname
    hostname = hostname.replace("https://", "")
    hostname = hostname.replace("http://", "")
    hostname = hostname.replace("www.", "")
    return hostname


@app.post("/admin/processing_run", status_code=200)
async def apply_processing_to_production(run_id: str):
    db = get_db()
    run_id = bson.ObjectId(run_id)

    crawling_runs = list(db.crawler_jobs.find({}, {"_id": 1, "templates": 1, "domain": 1}))

    processing_run = db.processing_runs.find_one({"_id": run_id})
    successful_runs = processing_run['processing_results']

    domain_map = {}
    for p in successful_runs:
        hostname = clean_hostname(p['url'])
        for r in crawling_runs:
            if hostname in r['domain']:
                domain_map[hostname] = r['templates'].get("product") # TODO make work for any template

    for run in successful_runs:
        db.products.update_one({"url": run['url']}, {"$set": run['product']}, upsert=True)
        hostname = clean_hostname(url=run['url'])
        scraping_data = domain_map.get(hostname)
        db.scraping_jobs.update_one({"url": run['url']}, {"$set": {"scraping_metadata": scraping_data, "parent": hostname}}, upsert=True)

    return "successfully applied processing run"



@app.put("/admin/domain/scraping-jobs")
def update_scraping_service(schema_change: dict, domain: str = Query(None)):
    db = get_db()

    if not schema_change.get("scraping_metadata"):
        raise HTTPException(status_code=400, detail="scraping metadata key not provided")

    result = db.scraping_jobs.update_many({"parent": domain},  {"$set": {"scraping_metadata": schema_change.get("scraping_metadata")}})

    return str(result.matched_count) + " updated successfully"


@app.get("/admin/get_scraping_errors")
def get_scraping_errors():
    db = get_db()
    return list(db.scraping_errors.find({})) # TODO change to str oid


@app.delete("/admin/remove-product")
def remove_product(product_id: str):
    """
    Removes product and scraping job for that product
    """
    db = get_db()
    product = db.products.find_one({"_id": bson.ObjectId(product_id)})
    if not product:
        raise HTTPException(status=404, detail="Product not found")

    scraping_job = db.scraping_jobs.find_one({"url": product['url']})


    db.products.delete_one({"_id": product_id})
    db.scraping_jobs.delete_one({"_id": scraping_job['_id']})



@app.post("/admin/products/prune")
def prune_scraping_jobs(delete: bool = Query(False)):
    """
    prunes scraping jobs and products if they're not associated

    Args:
        delete (bool) if delete is true will delete dangling products and scraping jobs
    Returns:
         dict: the scraping jobs and products that are dangling
    """
    db = get_db()
    projection = {"url": 1}
    scraping_jobs = list(db.scraping_jobs.find({}, projection))
    scraping_job_urls = [job['url'] for job in  scraping_jobs]

    products = list(db.products.find({}, projection))
    product_urls = [p['url'] for p in products]

    products_missing_jobs = []
    jobs_missing_products = []
    for p in products:
        if p['url'] not in scraping_job_urls:
            products_missing_jobs.append({
                "_id": str(p['_id']),
                "url": p['url']
            })

    for j in scraping_jobs:
        if j['url'] not in product_urls:
            jobs_missing_products.append({
                "_id": str(j['_id']),
                "url": j['url']
            })

    if delete:
        db.scraping_jobs.delete_many({"_id": {"$in": [bson.ObjectId(job['_id']) for job in jobs_missing_products]}})
        db.products.delete_many({"_id": {"$in": [bson.ObjectId(p['_id']) for p in products_missing_jobs]}})



    return {
        "products_missing_jobs": products_missing_jobs,
        "jobs_missing_products": jobs_missing_products,
        "deleted": delete
    }


@app.get("/admin/errors")
def get_errors():
    db = get_db()
    scraping_errors = list(db.scraping_errors.find({}))
    product_errors = list(db.products.find({"error": True}))

    for s in scraping_errors:
        s['_id'] = str(s['_id'])
    for p in product_errors:
        p['_id'] = str(p['_id'])

    return {
        "scraping_errors": scraping_errors,
        "product_errors": product_errors
    }


@app.post("/admin/schema")
def create_schema(schema: dict):
    print(schema)


@app.post("/admin/crawling-job")
def create_crawling_job():
    pass


