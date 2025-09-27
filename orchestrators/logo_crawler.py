import os
import asyncio
import httpx
from urllib.parse import quote_plus

STATIC_LOGOS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "logos")
os.makedirs(STATIC_LOGOS_DIR, exist_ok=True)

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

async def fetch_wikipedia_thumbnail(university_name: str, size:int=400):
    params = {
        "action": "query",
        "titles": university_name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": size
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(WIKIPEDIA_API, params=params)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for p in pages.values():
            thumb = p.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    return None

async def download_image_to_static(url: str, dest_filename: str):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        if r.status_code == 200:
            path = os.path.join(STATIC_LOGOS_DIR, dest_filename)
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    return None

async def duckduckgo_image_search(university_name: str):
    search_url = "https://api.duckduckgo.com/"
    params = {"q": f"{university_name} logo", "format": "json", "no_html": 1, "t": "myapp"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(search_url, params=params)
        data = r.json()
        return None

async def get_logo_for(university_name: str):
    safe_name = university_name.lower().replace(" ", "_")
    dest_filename = f"{safe_name}.png"
    dest_path = os.path.join(STATIC_LOGOS_DIR, dest_filename)
    if os.path.exists(dest_path):
        return dest_path

    try:
        thumb = await fetch_wikipedia_thumbnail(university_name)
    except Exception:
        thumb = None

    if thumb:
        saved = await download_image_to_static(thumb, dest_filename)
        if saved:
            return saved
    dd = await duckduckgo_image_search(university_name)
    if dd:
        saved = await download_image_to_static(dd, dest_filename)
        if saved:
            return saved

    return None
