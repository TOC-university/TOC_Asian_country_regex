import time
from typing import List, Set, Tuple, Optional
from utils.country import discover_country_pages
from utils.university import extract_universities_from_country_page
from utils.u_detail import extract_universities_detail_from_university_page
from config.settings import settings
from models import IndexUniversity

def crawl_countries() -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    slugs = sorted(mapping.keys())
    display = [s.replace("_", " ") for s in slugs]
    return display, slugs

def crawl_universities(
    min_count: Optional[int] = None,         
    limit: Optional[int] = None,             
    countries: Optional[List[str]] = None
) -> Tuple[List[IndexUniversity], List[str]]:
    mapping = discover_country_pages()
    names: List[IndexUniversity] = []
    sources: List[str] = []


    country_slugs = sorted(mapping.keys())
    if countries:
        want = {c.lower() for c in countries}
        country_slugs = [c for c in country_slugs if c.lower() in want]

    for slug in country_slugs:
        path = mapping[slug]
        chunk = extract_universities_from_country_page(path)
        before = len(names)

        for u in chunk:
            if limit is not None and len(names) >= limit:
                break
            abbr = u[1]
            if abbr == '':
                abbr = extract_universities_detail_from_university_page(u[2])['abbr']
            display = slug.replace("_", " ")
            names.append(IndexUniversity(name=u[0], abbreviation=abbr, country=display, path=u[2]))
            if limit is not None and len(names) >= limit:
                break

        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)
        if limit is not None and len(names) >= limit:
            break   
        # if min_count is not None and len(names) >= min_count:
        #     break

    result = sorted(names, key=lambda x: x.name)
    if limit is not None:
        result = result[:limit]
    return result, sources

def crawl_university_detail(university: str) -> dict:
    u_data = extract_universities_detail_from_university_page(university)
    # Placeholder for actual implementation
    # This function should fetch and return detailed information about the university
    return u_data
    