from fastapi import APIRouter, HTTPException
from depends import get_db

router = APIRouter()


@router.delete("/admin/remove-product")
def remove_product(product_id: str):
    """
    Removes product and scraping job for that product
    """
    db = get_db()
    product = db.products.find_one({"_id": bson.ObjectId(product_id)})
    if not product:
        raise HTTPException(status=404, detail="Product not found")

    scraping_job = db.scraping_jobs.find_one({"url": product['url']})


    db.products.delete_one({"_id": product_id})
    db.scraping_jobs.delete_one({"_id": scraping_job['_id']})
