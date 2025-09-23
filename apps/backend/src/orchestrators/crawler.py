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

def crawl_universities(        
    countries: Optional[List[str]] = None
) -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    names: Set[str] = set()
    sources: List[str] = []
    pairs: List[Tuple[str, str]] = []

    country_slugs = sorted(mapping.keys())
    if countries:
        want = {c.lower() for c in countries}
        country_slugs = [c for c in country_slugs if c.lower() in want]

    for slug in country_slugs:
        path = mapping[slug]
        country_name = slug.replace("_", " ").title()
        chunk = extract_universities_from_country_page(path)
        before = len(names)

        for uni in chunk:
            names.add(uni)
            pairs.append((uni, country_name))
        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)
        time.sleep(settings.SLEEP_SEC)

    result = sorted(names)
    seen = set(result)
    pairs = [(u, c) for (u, c) in pairs if u in seen]
    return result, sources, pairs
