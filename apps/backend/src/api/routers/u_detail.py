from fastapi import APIRouter, HTTPException
from models import UniversityRequest, UniversityResponse
from orchestrators.crawler import crawl_university_detail as crawl_university_detail_orch

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["u_detail"])

@router.post("/university")
async def crawl_university_detail(req: str):
    university = crawl_university_detail_orch(req)
    if university is None:
        raise HTTPException(status_code=404, detail="University not found")
    return university