from fastapi import APIRouter, HTTPException
from sympy import limit
from models import UniversitiesRequest, UniversitiesResponse, IndexUniversity
from typing import List, Tuple, Optional
import logging
from orchestrators import discover_country_pages
from utils.u_detail import extract_universities_detail_from_university_page
from config.settings import settings


from api.routers.search import Searcher
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawl", tags=["universities"])

@router.post("/universities", response_model=UniversitiesResponse)
async def crawl_universities_route(req: UniversitiesRequest):
    universities, sources = crawl_universities(
        countries=req.countries,
    )
    return UniversitiesResponse(count=len(universities), universities=universities, sources=sources)

def crawl_universities(        
        countries: Optional[List[str]] = None
    ) -> Tuple[List[IndexUniversity], List[str]]:            # University, Sources
    mapping = discover_country_pages()
    names: List[IndexUniversity] = []
    sources: List[str] = []
    pairs: List[Tuple[str, str]] = []
    seen = set()
    path_seen = set()
    country_slugs = sorted(mapping.keys())
    if countries:
        want = {c.lower() for c in countries}
        country_slugs = [c for c in country_slugs if c.lower() in want]

    for slug in country_slugs:
        path = mapping[slug]
        country_name = slug.replace("_", " ").title()
        before = len(names)

        for u in Searcher._phrases:
            if u.country.lower() != country_name.lower():
                continue
            if u.name in seen or u.path in path_seen:
                continue
            if not u.abbreviation:
                ud = extract_universities_detail_from_university_page(u.path)
                u.abbreviation, u.established, u.location, u.website, u.campuses, u.faculties = ud["abbr"], ud["estab"], ud["location"], ud["website"], ud["campuses"], ud["faculties"]
            display = slug.replace("_", " ")

            names.append(u)
            seen.add(u.name)
            path_seen.add(u.path)

        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)


    result = sorted(names, key=lambda x: x.name)
    return result, sources
