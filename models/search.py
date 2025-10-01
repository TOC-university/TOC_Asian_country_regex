from pydantic import BaseModel
from typing import List, Optional
from models import IndexUniversity

class SearchRequest(BaseModel):
    q: str
    k: int = 100
    rebuild: bool = False
    limit_units: int | None = None
    countries: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    suggestions: List[IndexUniversity]
    built_at: float | None = None
