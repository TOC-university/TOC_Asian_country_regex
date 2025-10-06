import time
from typing import List, Set, Tuple, Optional
from utils.country import discover_country_pages
from utils.university import extract_universities_from_country_page
from utils.u_detail import extract_universities_detail_from_university_page
from config.settings import settings
from models import IndexUniversity

import time
from typing import List, Set, Tuple, Optional
from utils.country import discover_country_pages
from utils.university import extract_universities_from_country_page
from config.settings import settings

from routers.search import Searcher as Searcher


def crawl_countries() -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    slugs = sorted(mapping.keys())
    display = [s.replace("_", " ") for s in slugs]
    return display, slugs

def crawl_universities_name(        
        countries: Optional[List[str]] = None
    ) -> Tuple[List[IndexUniversity], List[str], List[str]]:
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

        for u_name, u_path in chunk:
            if u_name in seen or u_path in path_seen:
                continue
            display = slug.replace("_", " ")
            
            names.append(IndexUniversity(name=u_name, country=display, path=u_path))
            pairs.append((u_name, country_name, u_path))
            seen.add(u_name)
            path_seen.add(u_path)

        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)

    result = sorted(names, key=lambda x: x.name)
    pairs = sorted(pairs, key=lambda x: x[0])
    return result, sources, pairs

def crawl_universities(        
        countries: Optional[List[str]] = None
    ) -> Tuple[List[IndexUniversity], List[str]]:            # University, Sources, Pairs
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
            seen.add(u_name)
            path_seen.add(u_path)

        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)


    result = sorted(names, key=lambda x: x.name)
    return result, sources

def crawl_university_detail(university: str) -> dict:
    u_data = extract_universities_detail_from_university_page(university)
    # Placeholder for actual implementation
    # This function should fetch and return detailed information about the university
    return u_data