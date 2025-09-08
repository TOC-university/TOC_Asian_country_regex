import time
from typing import List, Set, Tuple
from utils.country import discover_country_pages
from utils.university import extract_universities_from_country_page
from config.settings import settings

def crawl_countries() -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    slugs = sorted(mapping.keys())
    display = [s.replace("_", " ") for s in slugs]
    return display, slugs

def crawl_universities(min_count: int = 200, limit: int = 1000, countries: List[str] | None = None) -> Tuple[List[str], List[str]]:
    mapping = discover_country_pages()
    names: Set[str] = set()
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
            if len(names) >= limit:
                break
            names.add(n)
        if len(names) > before:
            src = path if path.startswith("http") else settings.BASE_URL + path
            sources.append(src)
        time.sleep(settings.SLEEP_SEC)
        if len(names) >= min_count:
            break

    return sorted(names)[:limit], sources
