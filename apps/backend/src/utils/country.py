import re, unicodedata
from typing import Dict, Iterable, Tuple
from .http import fetch
from config.settings import settings

A_TAG = r'<a[^>]*?href="/wiki/([^"#?:]+)"[^>]*>([^<]+)</a>'
ANCHOR = re.compile(A_TAG, re.I)
WHITES = re.compile(r"\s+")

def _clean(s: str) -> str:
    return WHITES.sub(" ", s).strip()

def _slugify(name: str) -> str:
    n = unicodedata.normalize("NFKD", name).replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_\-]", "", n)

def _extract_pairs(html: str) -> Iterable[Tuple[str, str]]:
    for href, text in ANCHOR.findall(html):
        yield href, _clean(text)

def discover_country_pages() -> Dict[str, str]:
    html = fetch(settings.START_PAGE)
    mapping: Dict[str, str] = {}
    pat = re.compile(r"(?i)\bList of (?:universities|colleges|universities and colleges) in ")
    for href, text in _extract_pairs(html):
        if not href.startswith("List_of_"):
            continue
        if pat.search(text) or pat.search(href.replace("_", " ")):
            country = re.sub(r"(?i)^List of (?:universities|colleges|universities and colleges) in ", "", text).strip()
            if not country:
                m = re.search(r"(?i)List_of_(?:universities|colleges|universities_and_colleges)_in_(.+)$", href)
                country = m.group(1).replace("_", " ") if m else href.replace("_", " ")
            mapping[_slugify(country)] = f"/wiki/{href}"
    return mapping
