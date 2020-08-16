from typing import List, Dict
from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field


class SelectorType(Enum):
    bool = "bool"
    string = "string"
    float = "float"


class SelectorStrategy(Enum):
    should_exist = "should_exist"
    not_exists = "not_exists"

class CrawlingStatus(Enum):
    pending = "pending"
    running = "running"
    complete = "complete"


class CrawlerTemplate(BaseModel):
    selector: str
    selector_strategy: SelectorStrategy
    selector_type: SelectorType



class CrawlerJobInput(BaseModel):
    start_url: str
    domain: str
    follow_keywords: List[str]
    templates: dict
    non_template_urls: list
    template_urls: list
    runs: list

class CrawlerJob(BaseModel):
    id: str = Field(..., alias='_id')
    start_url: str
    domain: str
    follow_keywords: List[str]
    templates: dict
    non_template_urls: list
    template_urls: list
    runs: list


class CrawlingQueue(BaseModel):
    id: str = Field(..., alias='_id')
    status: CrawlingStatus
    crawling_job_id: str

class CrawlingQueueInput(BaseModel):  
    status: CrawlingStatus
    crawling_job_id: str