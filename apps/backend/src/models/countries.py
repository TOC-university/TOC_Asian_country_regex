from pydantic import BaseModel
from typing import List

class Countries(BaseModel):
    count: int
    countries: List[str]
    country_slugs: List[str]
