from fastapi import APIRouter
from models import Countries
from orchestrators.crawler import crawl_countries

router = APIRouter(prefix="/crawl", tags=["countries"])

@router.get("/countries", response_model=list[Countries])
async def list_countries():
    display, slugs = crawl_countries()
    return [Countries(count=len(slugs), countries=display, country_slugs=slugs)]
