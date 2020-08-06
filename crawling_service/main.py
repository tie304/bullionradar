import scrapy
import sys
import datetime
from bson import ObjectId
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from src.parse import extract_templates

from depends import get_db

db = get_db()

job_queue = db.crawling_queue.find_one({"status": "pending"}) # get the first one in queue that pending
if not job_queue:
    print("no jobs found exiting.")
    sys.exit(0)

db.crawling_queue.update_one({"_id": ObjectId(job_queue['_id'])}, {"$set": {"status": "running"}})

job_id = job_queue['crawling_job_id']
job = db.crawler_jobs.find_one({"_id": ObjectId(job_id)})
FOLLOW_KEYWORDS = job['follow_keywords']
BASE_URL = "https://" + job['domain']
TEMPLATE_URL_BATCH_WRITE_LIMIT = 300

non_template_urls = []
template_urls = []
stats = None

process = CrawlerProcess()

class ProductDetect(scrapy.Spider):
    name = job['domain']
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
    }
    allowed_domains = [job['domain']]
    start_urls = [
        job['start_url'],
    ]

    def parse(self, response):
        global stats
        stats = self.crawler.stats.get_stats()
        page = response.url
        template_data = extract_templates(response.body, job)
        if template_data:
            template_data['domain'] = job['domain']
            template_data["url"] = page
            print(template_data)
            db.crawl_dump.update_one({"url": page}, {"$set": template_data}, upsert=True)
            template_urls.append(page)
        else:
            non_template_urls.append(page)

        if len(non_template_urls) >= TEMPLATE_URL_BATCH_WRITE_LIMIT or len(template_urls) >= TEMPLATE_URL_BATCH_WRITE_LIMIT:
            db.crawler_jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$addToSet": {"template_urls": {"$each": template_urls}}})
            db.crawler_jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$addToSet": {"non_template_urls": {"$each": non_template_urls}}})

            template_urls.clear()
            non_template_urls.clear()

        # get all links on page
        links = response.xpath('//a/@href').extract()
        # split links into keywords and determine if we want to follow them
        for link in links:
            link_keywords = []
            split = list(filter(None, link.split("/")))
            for el in split:
                if "-" in el:
                    second_split = el.split("-")
                    for sel in second_split:
                        link_keywords.append(sel)
                else:
                    link_keywords.append(el)
            if any(item in FOLLOW_KEYWORDS for item in link_keywords): # check for any keywords in list
                if BASE_URL not in link:
                    link = BASE_URL + link
                if link not in job['non_template_urls']: # dont search if we know its not a template we dont care about
                    yield scrapy.Request(link)


process.crawl(ProductDetect)
process.start()
db.crawler_jobs.update_one({"_id": ObjectId(job_id)}, {"$set": {"last_crawled": datetime.datetime.utcnow(),
                                                                "crawl_stats": stats}})
db.crawling_queue.update_one({"_id": ObjectId(job_queue['_id'])}, {"$set": {"status": "complete"}})