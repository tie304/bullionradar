import datetime
import time
from typing import List
import grequests
import traceback
from depends import _AppState, get_db
from src.extract_strategy import extract_data_from_html
from src.queueing import count_domains, generate_request_queue
from src.scraping_errors import write_scraping_error_to_db, ScrapingErrors

RES_TIMEOUT = 5
REQ_WAIT = 2 #seconds
START = time.time()

db = get_db()
scraping_jobs = list(db.scraping_jobs.find({}))
scraping_errors = list(db.scraping_errors.find({})) # TODO change to update job state instead
error_urls = [error['url'] for error in scraping_errors]
job_urls = [job['url'].strip("/") for job in scraping_jobs if job['url'] not in error_urls]

if not job_urls:
    raise Exception("No product urls found exiting")

# determine number of domains
domains: dict = count_domains(job_urls)
# orginize urls in batches of requests
batches: List[List[str]] = generate_request_queue(host_count=domains, url_list=job_urls)
print(f"provisioned: {sum(domains.values())} urls into {len(batches)} batches")
# maps for easy lookup
job_url_map = {}
for j in scraping_jobs:
    url = j['url'].strip("/")
    job_url_map[url] = j


# get all urls

for idx, batch in enumerate(batches):
    print(f"batch {idx} of {len(batches)}")
    

    # print(f"batch: {batch_start}:{batch_end} {len(job_urls)}")
    #job_urls_batch = job_urls[batch_start:batch_end] # ex 100
    #if not job_urls_batch:
        #break
    rs = []
    for url in batch:
        headers = job_url_map.get(url).get("headers")
        req = grequests.get(url, timeout=RES_TIMEOUT, headers=headers)
        rs.append(req)

    responses = grequests.map(rs)
    
    for idx, res in enumerate(responses):
        if res:
            job = job_url_map.get(res.url.strip("/"))
            if res.ok and job:
                try:
                    data: dict = extract_data_from_html(data=res.text, job=job)
                    data['scrape_update'] = datetime.datetime.utcnow()

                    db.products.update_one({"url": job['url']}, {"$set": data})

                except (ValueError, Exception) as e:
                    print("Error occurred processing html")
                    write_scraping_error_to_db(url=res.url, error_type=ScrapingErrors.HTML_PARSING_ERROR, msg=str(e), tb=traceback.format_exc())
            else:
                print("error occurred", res.url)
                write_scraping_error_to_db(url=res.url, error_type=ScrapingErrors.REQUEST_ERROR, tb=traceback.format_exc(), msg="bad response or could not find product in mapping")
        else:
            print("Error occurred res object is None or may have timed out: ", res)
            write_scraping_error_to_db(url=batch[idx], error_type=ScrapingErrors.REQUEST_ERROR, tb=traceback.format_exc(), msg="response object is none, may have timed out")

    time.sleep(REQ_WAIT)

db.scraping_runs.insert_one({
        "total_time": time.time() - START,
        "domains": list(domains.keys()),
        "total_urls": sum(domains.values()),
        "total_batches": len(batches)
    })









