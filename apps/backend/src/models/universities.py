from pydantic import BaseModel, Field, conlist
from typing import List, Optional

class UniversitiesRequest(BaseModel):
    countries: List[str] = Field(default_factory=list, description="Filter by country names")

class UniversitiesResponse(BaseModel):
    count: int
    names: List[str] | None
    sources: List[str] | None
    pairs: Optional[List[tuple[str, str]]] = None