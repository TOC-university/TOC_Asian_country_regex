from pydantic import BaseModel
from typing import List, Optional
from models import IndexUniversity

class SearchRequest(BaseModel):
    q: str
    k: int = 10
    rebuild: bool = False
    limit_units: int | None = None
    countries: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    suggestions: List[IndexUniversity]
    built_at: float | None = None

class PaginatedSearchRequest(BaseModel):
    q: str
    page: int = 1
    limit: int = 10
    rebuild: bool = False
    limit_units: int | None = None
    countries: Optional[List[str]] = None

class PaginatedSearchResponse(BaseModel):
    query: str
    suggestions: List[IndexUniversity]
    total: int
    page: int
    limit: int
    total_pages: int
    built_at: float | None = None