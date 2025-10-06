import os
import re
import asyncio
import httpx
from urllib.parse import quote_plus

# static directory for saved logos
STATIC_LOGOS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "logos")
os.makedirs(STATIC_LOGOS_DIR, exist_ok=True)

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

async def fetch_wikipedia_thumbnail(university_name: str, size: int = 400):
    """Use Wikipedia API to fetch the page thumbnail (if available).

    Returns the thumbnail URL string or None.
    """
    params = {
        "action": "query",
        "titles": university_name,
        "prop": "pageimages",
        "format": "json",
        "pithumbsize": size,
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(WIKIPEDIA_API, params=params)
            r.raise_for_status()
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for p in pages.values():
                thumb = p.get("thumbnail", {}).get("source")
                if thumb:
                    return thumb
    except Exception:
        return None
    return None


async def download_image_to_static(url: str, dest_filename: str):
    """Download image from `url` and save to STATIC_LOGOS_DIR with dest_filename.

    Returns saved path on success, otherwise None.
    """
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url)
            r.raise_for_status()
            path = os.path.join(STATIC_LOGOS_DIR, dest_filename)
            # write binary content
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except Exception:
        return None


async def get_logo_for(university_name: str):
    """Main entry: return path to saved logo image for `university_name`.

    - Sanitizes the university name using a regular expression to create a filesystem-safe filename.
    - Tries Wikipedia thumbnail first. (DuckDuckGo search removed as requested.)
    """
    # sanitize university name to a safe filename using regex
    # - lowercase
    # - replace any sequence of non-alphanumeric characters with underscore
    # - strip leading/trailing underscores
    safe_name = re.sub(r"[^a-z0-9]+", "_", university_name.lower()).strip("_")
    if not safe_name:
        safe_name = "unknown_university"

    dest_filename = f"{safe_name}.png"
    dest_path = os.path.join(STATIC_LOGOS_DIR, dest_filename)

    if os.path.exists(dest_path):
        return dest_path

    thumb = None
    try:
        thumb = await fetch_wikipedia_thumbnail(university_name)
    except Exception:
        thumb = None

    if thumb:
        saved = await download_image_to_static(thumb, dest_filename)
        if saved:
            return saved

    return None
