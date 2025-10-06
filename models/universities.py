from pydantic import BaseModel, Field, conlist
from typing import List, Optional, Tuple

class UniversitiesRequest(BaseModel):
    countries: List[str] = Field(default_factory=list, description="Filter by country names")

class IndexUniversity(BaseModel):
    name: str
    abbreviation: str | None = None
    country: str | None = None
    path: str | None = None
    website: str | None = None
    established: str | None = None
    location: str | None = None
    campuses: List[str] | None = None
    faculties: List[str] | None = None

class UniversitiesResponse(BaseModel):
    count: int
    universities: List[IndexUniversity] | None
    sources: List[str] | None

class UniversityRequest(BaseModel):
    university: str
