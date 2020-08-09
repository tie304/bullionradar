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


@app.post("/admin/apply/processing_run", status_code=200)
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



@app.put("/update/scraping-job-metadata")
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




