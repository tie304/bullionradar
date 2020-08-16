from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from src.models.crawler_jobs import CrawlerJobInput, CrawlingQueueInput, CrawlingQueue
from depends import get_db


router = APIRouter()


@router.put("/admin/crawler")
def update_crawler_job(job: CrawlerJobInput, crawler_id = Query(None)):
    db = get_db()

    result = db.crawler_jobs.find_one({"_id": ObjectId(crawler_id)})


    if not result:
        raise HTTPException(status_code=404, detail="crawling job not found")

    
    db.crawler_jobs.update_one({"_id": ObjectId(crawler_id)}, {"$set": job.dict()})
    update = db.crawler_jobs.find_one({"_id": ObjectId(crawler_id)})
    update["_id"] = str(update['_id'])

    return update


@router.post("/admin/crawler")
def create_crawling_job(job: CrawlerJobInput):
	db = get_db()

	result = db.crawler_jobs.find_one({"domain": job.domain})

	if result:
		raise HTTPException(status_code=400, detail="crawling job already exists")

	inserted_result = db.crawler_jobs.insert_one(job.dict())

	return str(inserted_result.inserted_id)




@router.delete("/admin/crawler/queue")
def enqueue_crawler_job(crawler_id: str = Query(None)):

	db = get_db()


	if not crawler_id:
		raise HTTPException(status_code=400, detail="no crawler id provided")

	crawling_job = db.crawling_queue.find_one({"crawling_job_id": crawler_id})

	if crawling_job:
		raise HTTPException(status_code=400, detail=f"crawling job already exists for crawling job {crawler_id}")

	queue = CrawlingQueueInput(crawling_job_id=crawler_id, status="pending")

	insert_result = db.crawling_queue.insert_one(queue.dict())

	return str(insert_result.inserted_id)


@router.get("/admin/crawler/queue")
def get_crawling_queue() -> CrawlingQueue:
	db = get_db()

	queue = list(db.crawling_queue.find({}))

	for q in queue:
		q['_id'] = str(q['_id']) # TODO fix 

	return [CrawlingQueue(**q) for q in queue]










