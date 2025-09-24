from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    q: str
    k: int = 10
    rebuild: bool = False
    limit_units: int | None = None
    countries: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    suggestions: List[str]
    built_at: float | None = None
