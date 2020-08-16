import bson
import time
from fastapi import FastAPI, File, UploadFile, HTTPException, Query

from src.routers import errors, processing_service, products, scraping_jobs, crawling_jobs

app = FastAPI()

app.include_router(errors.router)
app.include_router(processing_service.router)
app.include_router(products.router)
app.include_router(scraping_jobs.router)
app.include_router(crawling_jobs.router)




