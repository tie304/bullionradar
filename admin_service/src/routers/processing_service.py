from fastapi import APIRouter, HTTPException
from bson import ObjectId
from depends import get_db
from src.utils import clean_hostname

router = APIRouter()

@router.get("/processing-runs")
def get_processing_runs():
    """
    Returns all processing  runs excluding run data
    """
    db = get_db()
    projection = {"processing_errors": 0, "processing_results": 0}
    results = list(db.processing_runs.find({}, projection))
    for i in results:
        i['_id'] = str(i['_id'])

    return results




@router.post("/admin/apply-processing-run", status_code=201)
def apply_processing_to_production(run_id: str):
    db = get_db()
    run_id = ObjectId(run_id)

    crawling_runs = list(db.crawler_jobs.find({}, {"_id": 1, "templates": 1, "domain": 1}))

    processing_run = db.processing_runs.find_one({"_id": run_id})
    successful_runs = processing_run['processing_results']
    scraping_jobs = []
    products = []

    domain_map = {}
    for p in successful_runs:
        hostname = clean_hostname(p['url'])
        for r in crawling_runs:
            if hostname in r['domain']:
                domain_map[hostname] = r['templates'].get("product") # TODO make work for any template


    for run in successful_runs:
        hostname = clean_hostname(url=run['url'])
        scraping_data = domain_map.get(hostname)

        scraping_jobs.append({
                "url": run['url'],
                "scraping_metadata": scraping_data,
                "parent": hostname
            })
        product = run.get("product")
        product["url"] = run["url"]
        products.append(product)
    


    db.products.insert_many(products)
    db.scraping_jobs.insert_many(scraping_jobs)
    db.processing_runs.update_one({"_id": run_id}, {"$set": {"applied": True}})

    return "successfully applied processing run"


@router.delete("/admin/apply-processing-run", status_code=201)
def unapply_processing_run(run_id: str):
    db = get_db()
    urls = []
    projection = {"processing_errors": 0, "processing_results": 0}
    # do checks first so the db doesnt need to work as hard
    result = db.processing_runs.find_one({"_id": ObjectId(run_id)}, projection)
    if not result:
        raise HTTPException(status_code=404, detail="Processing run not found")
    # needs to have been applied in order to be un-applied
    if not result.get("applied"):
        raise HTTPException(status_code=400, detail="Processing run not applied")
    #then grab all
    result = db.processing_runs.find_one({"_id": ObjectId(run_id)})
    for i in result['processing_results']:
        urls.append(i['url'])

    # delete scraping job and products
    db.scraping_jobs.delete_many({"url": {"$in": urls}})
    db.products.delete_many({"url": {"$in": urls}})

    result = db.processing_runs.update_one({"_id": ObjectId(run_id)}, {"$set": {"applied": False}})


    return "processing run successfully un-applyed"




