import time
from typing import List, Set, Tuple, Optional
from utils.country import discover_country_pages
from utils.university import extract_universities_from_country_page
from utils.u_detail import extract_universities_detail_from_university_page
from config.settings import settings

def crawl_countries() -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    slugs = sorted(mapping.keys())
    display = [s.replace("_", " ") for s in slugs]
    return display, slugs

def crawl_universities(
    min_count: Optional[int] = None,         
    limit: Optional[int] = None,             
    countries: Optional[List[str]] = None
) -> Tuple[List[Tuple[str, str]], List[str]]:
    mapping = discover_country_pages()
    names: List[Tuple[str, str]] = []
    sources: List[str] = []


    country_slugs = sorted(mapping.keys())
    if countries:
        want = {c.lower() for c in countries}
        country_slugs = [c for c in country_slugs if c.lower() in want]

    for slug in country_slugs:
        path = mapping[slug]
        chunk = extract_universities_from_country_page(path)
        before = len(names)

        for n in chunk:
            if limit is not None and len(names) >= limit:
                break
            names.append(n)
        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)
            
        if min_count is not None and len(names) >= min_count:
            break

    result = sorted(names, key=lambda x: x[0])
    if limit is not None:
        result = result[:limit]
    return result, sources

def crawl_university_detail(university: str) -> dict:
    result = {}
    # Placeholder for actual implementation
    # This function should fetch and return detailed information about the university
    return extract_universities_detail_from_university_page(university)
    return {
        "name": university,
        "aka": "Example University",
        "website": "http://www.example.edu",
        "establishedAt": 1900,
        "mainCampus": {
            "address": "123 University St, City, Country",
            "coordinates": {"lat": 0.0, "lng": 0.0}
        }
    }