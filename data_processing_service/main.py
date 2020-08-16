import inspect
import time
import datetime
import sys
from typing import Any
import traceback

from depends import get_db
from src.processing_strategies.return_self import return_self
from src.processing_strategies.find_metal_type import find_metal_type
from src.processing_strategies.find_metal_form import find_metal_form
from src.processing_strategies.find_metal_size import find_metal_size

PROCESSING_BATCH = 100
PROCESSING_STRATEGY = {
    "input_schemas": {
        "product": {
            "required": {
                "title": str,
                "stock": bool,
                "price": float
            },
            "optional": {
                "description": str
            }
        }
    },
    "output_schema": {
        "required": {
            "title": str,
            "price": float,
            "stock": bool,
            "metal_type": str,
            "metal_form": str,
            "metal_size_unit": str
        },
        "optional": {
            "description": str
        }
    },
    "processing_strategy": {
        "product": {
            "title": None,
            "price": None,
            "description": None,
            "stock": None,
            "metal_type": "find_metal_type",
            "metal_form": "find_metal_form",
            "metal_size_unit": "find_metal_size"
        }

    }
}

STRATEGY_MAP = {
    "find_metal_type": find_metal_type,
    "find_metal_form": find_metal_form,
    "find_metal_size": find_metal_size,
}

def dispatch_processing_strategy(document: dict, processing_strategy: dict):
    """
    Calls required function that will map to schema.

    Args:
        document (dict): document from input schema
        processing_strategy (dict): strategy for processing each field

    """
    result = {}
    result['url'] = document.get("url")
    for s in processing_strategy:
        result[s] = {}
        for k,v in processing_strategy[s].items():
            fn = STRATEGY_MAP.get(v) # get function
            if not fn: # if not function set the current value
                result[s][k] = document[s].get(k)
                continue

            arg_ref = inspect.getfullargspec(fn).args # get args from processing function

            args = {}
            for a in arg_ref: # create dict of args
                arg = document[s].get(a)
                args[a] = arg

            result[s][k] = fn(**args) # call fn with args
    return result


def validate_schema(object, schema):
    assert "url" in object, "missing url"
    for t in schema.keys():
        assert object.get(t), "incorrect schema error"
        for r in schema[t]['required']:
            assert r in object.get(t), f"missing required field, {r}"
        for k,v in object.get(t).items():
            if schema[t]['required'].get(k):
                assert isinstance(v, schema[t]['required'][k]), f"incorrect type {v} for {schema[t]['required'][k]}"
            if schema[t]['optional'].get(k):
                assert isinstance(v, schema[t]['optional'][k]),  f"incorrect type {v} for {schema[t]['optional'][k]}"


SKIP = 0
db = get_db()
processing_results = [] # results stored for batch insert later
processing_errors = [] # errors relating to processing
start = time.time()
print("processing...")
while True:
    data = list(db.crawl_dump.find().skip(SKIP).limit(PROCESSING_BATCH)) # curser object  is read once. need to cast to list
    print(SKIP,  "-", SKIP + PROCESSING_BATCH)
    data_length = len(data)
    if data_length == 0:
        break
    for d in data:
        try:
            validate_schema(d, schema=PROCESSING_STRATEGY['input_schemas'])
        except Exception as e:
            processing_errors.append({
                "error_msg": str(e),
                "error_type": "validation pipeline error",
                "document": d
            })
            continue
        try:
            result = dispatch_processing_strategy(d, processing_strategy=PROCESSING_STRATEGY['processing_strategy'])
        except Exception as e:
            processing_errors.append({
                "error_msg": str(e),
                "error_type": "dispatching pipeline error",
                "document": d
            })
            continue
        processing_results.append(result)
    SKIP += PROCESSING_BATCH

db.processing_runs.insert_one({
    "run_time_seconds": time.time() - start,
    "total_documents_processed": len(processing_results) + len(processing_errors),
    "total_processing_errors": len(processing_errors),
    "processing_errors": processing_errors,
    "processing_results": processing_results,
    "date": datetime.datetime.utcnow(),
    "applied": False
})