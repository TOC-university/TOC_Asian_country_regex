from fastapi import APIRouter, HTTPException
from models import UniversityRequest, IndexUniversity
from orchestrators.crawler import crawl_university_detail as crawl_university_detail_orch

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["u_detail"])

@router.post("/university")
async def crawl_university_detail(path: str):
    university = crawl_university_detail_orch(path)
    return university