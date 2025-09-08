import re
from typing import List, Tuple
from .http import fetch

A_TAG = r'<a[^>]*?href="/wiki/([^"#?:]+)"[^>]*>([^<]+)</a>'
ANCHOR = re.compile(A_TAG, re.I)
BRACKET = re.compile(r"\s*\([^)]*\)\s*")
FOOTNOTE = re.compile(r"\[\d+\]")
WHITES = re.compile(r"\s+")

KEYWORDS = re.compile(
    r"(?i)\b(University|College|Institute|Academy|Polytechnic|Universidad|Universität|Université|มหาวิทยาลัย|วิทยาลัย)\b"
)

def _clean(s: str) -> str:
    s = FOOTNOTE.sub("", s)
    s = BRACKET.sub("", s)
    s = WHITES.sub(" ", s).strip(" \t\n\r-–—")
    return s

def extract_universities_from_country_page(path: str) -> List[str]:
    html = fetch(path)
    names: List[str] = []
    for _, text in ANCHOR.findall(html):
        t = _clean(text)
        if len(t) < 3: 
            continue
        if "List of" in t or "Category:" in t:
            continue
        if KEYWORDS.search(t):
            names.append(t)
    if len(names) < 50:
        names = [_clean(t) for _, t in ANCHOR.findall(html) if len(_clean(t)) >= 3]
    return names
