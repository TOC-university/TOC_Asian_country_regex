from __future__ import annotations
import unicodedata, re, time, threading
from typing import List, Tuple
from utils.country import discover_country_pages
from utils.university import extract_universities_from_country_page
from orchestrators.crawler import crawl_universities
from config.settings import settings

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def display_slug(slug: str) -> str:
    return slug.replace("_", " ").replace("-", " ").strip().title()

class Searcher:
    def __init__(self):
        self._lock = threading.Lock()
        self._pharses: List[str] = []
        self._normalizes: List[str] = []
        self._built_at: float | None = None
    def build(self, limit_units: int | None = None, countries: List[str] | None = None) -> None:
        mapping = discover_country_pages()
        phrases: List[str] = [display_slug(s) for s in sorted(mapping.keys()) ]
        
        _, _, pairs = crawl_universities(countries=countries)

        for uni, country in pairs:
            phrases.append(f"{uni} ({country})")

        normalizes = [_norm(p) for p in phrases]
        with self._lock:
            self._phrases = phrases
            self._normalizes = normalizes
            self._built_at = time.time()
    def search(self, query: str, k: int = 10) -> List[str]:
        query_norm = _norm(query)
        if not query_norm:
            return []
        with self._lock:
            phrases = self._phrases
            normalizes = self._normalizes
        
        results: List[str] = []
        seen = set()
        for phrase, norm in zip(phrases, normalizes):
            tokens = norm.split()
            if tokens and tokens[0].startswith(query_norm):
                if phrase not in seen:
                    seen.add(phrase)
                    results.append(phrase)
            if len(results) >= k:
                break
        return results
