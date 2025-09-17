import re
from typing import List, Tuple
from .http import fetch

A_TAG = re.compile(r'<a[^>]*?href="([^"#?]+)"[^>]*>([^<]+)</a>')
BRACKET = re.compile(r"\s*\([^)]*\)\s*")
FOOTNOTE = re.compile(r"\[\d+\]")
WHITES = re.compile(r"\s+")

KEYWORDS = re.compile(
    r"(?i)\b("
    r"University|College|Institute|Polytechnic|Academy|Faculty|School"
    r"|Universidad|Instituto|Escuela|Politécnico|Tecnológico|Tecnológica"
    r")\b"
)

def _clean(s: str) -> str:
    s = FOOTNOTE.sub("", s)
    s = BRACKET.sub("", s)
    s = WHITES.sub(" ", s).strip(" \t\n\r-–—")
    return s

def extract_universities_detail_from_university_page(path: str) -> dict:
    html = fetch(path)
    info = {}
    #abbr from website or just appear 
    a = A_TAG.findall(html)
    for url, text in a:
        t = _clean(url)
        if len(t) < 3: 
            continue
        if "List of" in t or "Category:" in t:
            continue
        if KEYWORDS.search(t):
            names.append(t)
    if len(names) < 50:
        names = [_clean(t) for _, t in ANCHOR.findall(html) if len(_clean(t)) >= 3]
    return names
    
    return info