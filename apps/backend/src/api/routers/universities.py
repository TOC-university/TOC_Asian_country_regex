from fastapi import APIRouter
from sympy import limit
from models import UniversitiesRequest, UniversitiesResponse
from orchestrators.crawler import crawl_universities
from typing import List, Tuple
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["universities"])

@router.post("/universities", response_model=UniversitiesResponse)
async def crawl_universities(REQUEST: UniversitiesRequest):
    try:
        names, sources = crawl_universities(
            min_count=REQUEST.min_count,
            limit=REQUEST.limit,
            countries=REQUEST.countries,
        )
        return UniversitiesResponse(count=len(names), names=names, sources=sources)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return UniversitiesResponse(count=0, names=[str(e)], sources=[""])
    # return UniversitiesResponse(count=len(names), names=names, sources=sources)
# async def crawl_universities(req: UniversitiesRequest):
#     names, sources = crawl_universities(
#         min_count=req.min_count,
#         limit=req.limit,
#         countries=req.countries,
#     )
#     return UniversitiesResponse(count=len(names), names=names, sources=sources)
