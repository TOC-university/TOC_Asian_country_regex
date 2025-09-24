from fastapi import APIRouter
from sympy import limit
from models import UniversitiesRequest, UniversitiesResponse
from orchestrators.crawler import crawl_universities as crawl_universities_orch
from typing import List, Tuple
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["universities"])

@router.post("/universities", response_model=UniversitiesResponse)
async def crawl_universities_route(req: UniversitiesRequest):
    names, sources, pairs = crawl_universities_orch(
        countries=req.countries,
    )
    return UniversitiesResponse(count=len(names), names=names, sources=sources)
