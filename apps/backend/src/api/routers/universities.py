from fastapi import APIRouter, HTTPException
from sympy import limit
from models import UniversitiesRequest, UniversitiesResponse
from orchestrators.crawler import crawl_universities as crawl_universities_orch
from typing import List, Tuple
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["universities"])

@router.post("/universities", response_model=UniversitiesResponse)
async def crawl_universities_route(req: UniversitiesRequest):
    names, sources = crawl_universities_orch(
        min_count=req.min_count,
        limit=req.limit,
        countries=req.countries,
    )
    if req.limit is not None:
        names = names[:req.limit]
    return UniversitiesResponse(count=len(names), names=names, sources=sources)

# @router.post("/university", response_model=UniversityResponse)
# async def get_university_route(req: UniversityRequest):
#     university: UniversityResponse = await crawl_university_info_orch(req.university)
#     if university is None:
#         raise HTTPException(status_code=404, detail="University not found")
#     return university
