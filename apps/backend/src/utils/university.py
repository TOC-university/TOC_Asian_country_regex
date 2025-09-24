import re
from typing import List, Tuple
from .http import fetch

A_TAG = r'<a[^>]*?href="(/wiki/[^"#?:]+)"[^>]*>([^<]+)</a>'
AFTER_A = r'([^<]*?)'
ANCHOR = re.compile(A_TAG, re.I)
BRACKET = re.compile(r"\s*\(([^)]*)\)\s*")
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

def extract_universities_from_country_page(path: str) -> List[Tuple[str, str, str]]:        #name abbreviate path
    print('fetching', path)
    html = fetch(path)
    names: List[Tuple[str, str, str]] = []

    matched_anchor = ANCHOR.findall(html)
    for u_path, text in matched_anchor:
        possible_abbr = BRACKET.findall(text)
        t, a = _clean(text), possible_abbr[0] if possible_abbr else ''
        if len(t) < 3: 
            continue
        if "List of" in t or "Category:" in t:
            continue
        if KEYWORDS.search(t):
            if t not in [tt for tt, _, _ in names]:
                names.append((t, a, u_path))
    # if len(names) < 50:
    #     names = [(_clean(t), _clean(''), u_path) for u_path, t in ANCHOR.findall(html) if len(_clean(t)) >= 3]
    return names
