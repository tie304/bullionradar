from fastapi import FastAPI, File, UploadFile, HTTPException
from src.validate import validate_csv, validate_requests
from src.persist import create_products, create_scraping_jobs



app = FastAPI()



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