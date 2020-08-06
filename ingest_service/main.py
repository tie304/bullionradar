import bson
import time
import urllib.parse as urlparse
from depends import get_db
from fastapi import FastAPI, File, UploadFile, HTTPException
from src.validate import validate_csv, validate_requests
from src.persist import create_products, create_scraping_jobs



app = FastAPI()

def clean_hostname(url):
    hostname = urlparse.urlparse(url).hostname
    hostname = hostname.replace("https://", "")
    hostname = hostname.replace("http://", "")
    hostname = hostname.replace("www.", "")
    return hostname


@app.post("/ingest/csv", status_code=201)
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    csv_str = contents.decode("utf-8")

    try:
        validate_csv(csv_str)
    except AssertionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="error in csv validation pipeline: " + str(e))

    try:
        validate_requests(csv_str)
    except AssertionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="error in request validation pipeline: " + str(e))

    try:
        create_products(csv_str)
        create_scraping_jobs(csv_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail="error persisting " + str(e))

    return {"success": file.filename + " has passed validation and successfully uploaded"}


@app.post("/apply/run", status_code=200)
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



