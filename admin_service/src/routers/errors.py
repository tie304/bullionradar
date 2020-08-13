from fastapi import APIRouter, HTTPException
from depends import get_db

router = APIRouter()


@router.get("/admin/errors")
def get_errors():
    db = get_db()
    scraping_errors = list(db.scraping_errors.find({}))
    product_errors = list(db.products.find({"error": True}))

    for s in scraping_errors:
        s['_id'] = str(s['_id'])
    for p in product_errors:
        p['_id'] = str(p['_id'])

    return {
        "scraping_errors": scraping_errors,
        "product_errors": product_errors
    }

