from fastapi import APIRouter, HTTPException
from sympy import limit
from models import UniversitiesRequest, UniversitiesResponse
from orchestrators.search import crawl_universities as crawl_universities_orch
from typing import List, Tuple
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["universities"])

@router.post("/universities", response_model=UniversitiesResponse)
async def crawl_universities_route(req: UniversitiesRequest):
    universities, sources, pairs = crawl_universities_orch(
        countries=req.countries,
    )
    return UniversitiesResponse(count=len(universities), universities=universities, sources=sources)

# @router.post("/university", response_model=UniversityResponse)
# async def get_university_route(req: UniversityRequest):
#     university: UniversityResponse = await crawl_university_info_orch(req.university)
#     if university is None:
#         raise HTTPException(status_code=404, detail="University not found")
#     return university
