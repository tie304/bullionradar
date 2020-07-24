from typing import Union
from bson import ObjectId


def object_id_converter(item: Union[list, dict]):
    if isinstance(item, list):
        for i in item:
            if isinstance(i, dict):
                for k,v in i.items():
                    if isinstance(i[k], ObjectId):
                        i[k] = str(i[k])
            if isinstance(i, list):
                object_id_converter(i)
    return item


