from pydantic import BaseModel, Field, conlist
from typing import List, Optional

class UniversitiesRequest(BaseModel):
    min_count: int = Field(0, ge=0, description="Minimum universities to collect")
    limit: int | None = Field(None, ge=1, description="Optional cap on number returned")
    countries: List[str] = Field(default_factory=list, description="Filter by country names")

class UniversitiesResponse(BaseModel):
    count: int
    names: List[str] | None
    sources: List[str] | None