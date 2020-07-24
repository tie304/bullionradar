from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class Sizes(str, Enum):
    one_gram = "1g"
    two_and_half_gram = "2.5g"
    one_ounce = "1oz"
    five_ounce = "5oz"
    ten_ounce = "10oz"


class PriceSort(str, Enum):
    gte = "gte"
    lte = "lte"


class Metals(str, Enum):
    gold = "gold"
    silver = "silver"


class PriceFilter(BaseModel):
    type: PriceSort
    price: float


class ProductSearch(BaseModel):
    price: Optional[PriceFilter]
    metals: Optional[List[Metals]]
    size: Optional[Sizes]
