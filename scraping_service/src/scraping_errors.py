import datetime
from enum import Enum
from depends import get_db


class ScrapingErrors(str, Enum):
    HTML_PARSING_ERROR = "html_parsing_error"
    REQUEST_ERROR = "request_error"


def write_scraping_error_to_db(msg: str, url: str, error_type: ScrapingErrors, tb:str, db = get_db()) -> None:
    """
    Create scraping error and write to db. Also flag product so it wont show up in search
    """
    db.scraping_errors.insert_one({
        "msg": msg,
        "url": url,
        "tb": tb,
        "error_type": error_type,
        "time": datetime.datetime.utcnow()
    });

    db.products.update_one({"url": url}, {"$set": { "error": True}})