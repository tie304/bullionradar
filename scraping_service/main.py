import datetime
import grequests
import traceback
from depends import _AppState, get_db
from src.extract_strategy import extract_data_from_html, extract_spot_from_html
from src.scraping_errors import write_scraping_error_to_db, ScrapingErrors

RES_TIMEOUT = 5
REQ_BATCH = 100

db = get_db()
scraping_jobs = list(db.scraping_jobs.find({}))
scraping_errors = list(db.scraping_errors.find({})) # TODO change to update job state instead
error_urls = [error['url'] for error in scraping_errors]
job_urls = [job['url'] for job in scraping_jobs if job['url'] not in error_urls]

if not job_urls:
    raise Exception("No product urls found exiting")

# maps for easy lookup
job_url_map = {}
for j in scraping_jobs:
    url = j['url']
    job_url_map[url] = j

print(f"starting batch url fetching: {len(job_urls)} at {REQ_BATCH} each ")
# get all urls
batch_start = 0
while True:
    print(f"batch: {batch_start}:{REQ_BATCH} {len(job_urls)}")
    job_urls_batch = job_urls[batch_start:REQ_BATCH] # ex 100
    if not job_urls_batch:
        break

    rs = []

    for u in job_urls_batch:
        headers = job_url_map.get(u).get("headers")
        r = grequests.get(u, timeout=RES_TIMEOUT, headers=headers)
        rs.append(r)

    responses = grequests.map(rs)

    for idx, res in enumerate(responses):
        if res:
            job = job_url_map.get(res.url.strip("/"))
            if res.ok and job:
                try:
                    data = extract_data_from_html(data=res.text, job=job)
                    data['spot_update'] = datetime.datetime.utcnow()

                    if job.get("type") == "product":
                        db.products.update_one({"url": job['url']}, {"$set": data})

                except (ValueError, Exception) as e:
                    print("Error occurred processing html")
                    write_scraping_error_to_db(url=res.url, error_type=ScrapingErrors.HTML_PARSING_ERROR, msg=str(e), tb=traceback.format_exc())
            else:
                print("error occurred", res.url)
                write_scraping_error_to_db(url=res.url, error_type=ScrapingErrors.REQUEST_ERROR, tb=traceback.format_exc(), msg="bad response or could not find product in mapping")
        else:
            print("Error occurred res object is None or may have timed out")
            write_scraping_error_to_db(url=job_urls[idx], error_type=ScrapingErrors.REQUEST_ERROR, tb=traceback.format_exc(), msg="response object is none, may have timed out")

    batch_start += REQ_BATCH











