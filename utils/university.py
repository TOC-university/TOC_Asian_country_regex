import re
from typing import List, Tuple
from .http import fetch

A_TAG = r'<a[^>]*?href="(/wiki/[^"#?:]+)"[^>]*>([^<]+)</a>'
AFTER_A = r'([^<]*?)'
ANCHOR = re.compile(A_TAG, re.I)
BRACKET = re.compile(r"\s*\(([^)]*)\)\s*")
FOOTNOTE = re.compile(r"\[\d+\]")
WHITES = re.compile(r"\s+")

INSTITUTION_KEYWORDS = re.compile(
    r"(?i)\b("
    r"University|College|Institute|Polytechnic|Academy|Faculty|School"
    r"|Universidad|Instituto|Escuela|Politécnico|Tecnológico|Tecnológica"
    r")\b"
)

GENERIC_SLUGS = {
    "University", "College", "Institute", "Academy", "Faculty", "School",
    "University_system", "University_systems", "National_key_university",
    "University_(hierarchy)", "University_(disambiguation)",
    "Higher_education", "List_of_universities", "College_(disambiguation)"
}
GENERIC_TEXT_EXACT = {
    "university", "college", "institute", "academy", "faculty", "school",
    "university system", "university systems", "national key university"
}
GENERIC_TEXT_CONTAINS = re.compile(r"(?i)\b(List of|Category:)\b")

SLUG_LOOKS_INSTITUTION = re.compile(
    r"(?x)"
    r"(?:"
    r"^[A-Z][A-Za-z0-9\-_%]+_(University|College|Institute|Academy|Faculty|School)\b"
    r"|^(University|College|Institute|Academy|Faculty|School)_of_[A-Z]"
    r")"
)

def _clean(s: str) -> str:
    s = FOOTNOTE.sub("", s)
    s = BRACKET.sub("", s)
    s = WHITES.sub(" ", s).strip(" \t\n\r-–—")
    return s

def _is_generic(slug: str, text: str) -> bool:
    if slug in GENERIC_SLUGS:
        return True
    t = text.strip().lower()
    if t in GENERIC_TEXT_EXACT:
        return True
    if GENERIC_TEXT_CONTAINS.search(text):
        return True
    return False

def extract_universities_from_country_page(path: str) -> List[Tuple[str, str, str]]:        #name abbreviate path
    print('fetching', path)
    html = fetch(path)
    seen = set()
    result: List[Tuple[str, str, str]] = []

    matched_anchor = ANCHOR.findall(html)
    for u_path, raw_text in matched_anchor:
        possible_abbr = BRACKET.findall(raw_text)
        text, abbreviate = _clean(raw_text), possible_abbr[0] if possible_abbr else ''


        if len(text) < 3: 
            continue
        if not INSTITUTION_KEYWORDS.search(text):
            continue
        if _is_generic(u_path, text):
            continue
        if not SLUG_LOOKS_INSTITUTION.search(u_path):
            if not re.search(r"(?i)\b(University|College|Institute|Academy|Faculty|School)\b", text):
                continue
            if re.fullmatch(r"(?i)\b(University|College|Institute|Academy|Faculty|School)s?\b", text):
                continue
            if re.search(r"(?i)\b(system|systems|ranking|education|students?)\b", text):
                continue

        if text not in seen:
            seen.add(text)
            result.append((text, abbreviate, u_path))

    return result
