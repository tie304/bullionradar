from fastapi import APIRouter, HTTPException, Query
from depends import get_db


router = APIRouter()


@router.put("/scraping-jobs/bulk")
def update_scraping_service(schema_change: dict, domain: str = Query(None)):
    db = get_db()

    # TODO validate schema

    if not schema_change.get("scraping_metadata"):
        raise HTTPException(status_code=400, detail="scraping metadata key not provided")

    result = db.scraping_jobs.update_many({"parent": domain},  {"$set": {"scraping_metadata": schema_change.get("scraping_metadata")}})

    return str(result.matched_count) + " updated successfully"


@router.post("/scraping-jobs/prune")
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
