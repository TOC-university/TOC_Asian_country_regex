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
    country_slugs = sorted(mapping.keys())
    if countries:
        want = {c.lower() for c in countries}
        country_slugs = [c for c in country_slugs if c.lower() in want]

    for slug in country_slugs:
        path = mapping[slug]
        country_name = slug.replace("_", " ").title()
        chunk = extract_universities_from_country_page(path)
        before = len(names)


        for u_name, u_path in chunk:
            if u_name in seen:
                continue
            display = slug.replace("_", " ")
            
            names.append(IndexUniversity(name=u_name, country=display, path=u_path))
            pairs.append((u_name, country_name, u_path))
            seen.add(u_name)

        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)


    result = sorted(names, key=lambda x: x.name)
    pairs = [(u, c, p) for (u, c, p) in pairs if u in sorted(seen)]
    return result, sources, pairs

def crawl_countries() -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    slugs = sorted(mapping.keys())
    display = [s.replace("_", " ") for s in slugs]
    return display, slugs

def crawl_universities(        
    countries: Optional[List[str]] = None
) -> Tuple[List[IndexUniversity], List[str], List[str]]:            # University, Sources, Pairs
    mapping = discover_country_pages()
    names: List[IndexUniversity] = []
    sources: List[str] = []
    pairs: List[Tuple[str, str]] = []
    seen = set()
    country_slugs = sorted(mapping.keys())
    if countries:
        want = {c.lower() for c in countries}
        country_slugs = [c for c in country_slugs if c.lower() in want]

    for slug in country_slugs:
        path = mapping[slug]
        country_name = slug.replace("_", " ").title()
        chunk = extract_universities_from_country_page(path)
        before = len(names)

        for u_name, u_path in chunk:
            if u_name in seen:
                continue
            abbreviate = extract_universities_detail_from_university_page(u_path, ['abbreviate'])['abbr']
            display = slug.replace("_", " ")
            
            names.append(IndexUniversity(name=u_name, abbreviation=abbreviate, country=display, path=u_path))
            print(f'fetched university: {len(names)}')
            pairs.append((u_name, country_name, u_path))
            seen.add(u_name)

        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)
        time.sleep(settings.SLEEP_SEC)


    result = sorted(names, key=lambda x: x.name)
    pairs = [(u, c, p) for (u, c, p) in pairs if u in sorted(seen)]
    return result, sources, pairs

def crawl_university_detail(university: str) -> dict:
    u_data = extract_universities_detail_from_university_page(university)
    # Placeholder for actual implementation
    # This function should fetch and return detailed information about the university
    return u_data