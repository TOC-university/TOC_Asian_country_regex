import requests
from config.settings import settings

def fetch(path_or_url: str) -> str:
    url = path_or_url if path_or_url.startswith("http") else settings.BASE_URL + path_or_url
    r = requests.get(url, headers={"User-Agent": settings.USER_AGENT}, timeout=settings.TIMEOUT)
    r.raise_for_status()
    return r.text
