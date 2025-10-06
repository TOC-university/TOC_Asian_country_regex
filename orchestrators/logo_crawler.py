# File: orchestrators/logo_crawler.py
import os
import re
import html
import asyncio
import httpx
from utils  .http import fetch

STATIC_LOGOS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "logos")
os.makedirs(STATIC_LOGOS_DIR, exist_ok=True)

async def fetch_wikipedia_html(university_name: str) -> str:
    # Convert name to Wikipedia-friendly URL
    safe_name = university_name.replace(' ', '_').replace("'", "’")
    url = f"https://en.wikipedia.org/wiki/{safe_name}"
    html_content = await asyncio.to_thread(fetch, url)
    return html_content

async def download_image_to_static(url: str, dest_filename: str):
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        if r.status_code == 200:
            path = os.path.join(STATIC_LOGOS_DIR, dest_filename)
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    return None

async def get_logo_for(university_name: str):
    safe_name = re.sub(r"[^a-z0-9]+", "_", university_name.lower()).strip("_")
    if not safe_name:
        safe_name = "unknown_university"
    dest_filename = f"{safe_name}.png"
    dest_path = os.path.join(STATIC_LOGOS_DIR, dest_filename)

    if os.path.exists(dest_path):
        return dest_path

    html_content = await fetch_wikipedia_html(university_name)

    # Try to extract thumbnail from infobox
    thumb_match = re.search(r'<table class="infobox.*?">.*?<img[^>]*src="([^"]+)"', html_content, re.S)
    if thumb_match:
        thumb_url = thumb_match.group(1)
        if thumb_url.startswith('//'):
            thumb_url = 'https:' + thumb_url
        saved = await download_image_to_static(thumb_url, dest_filename)
        if saved:
            return saved

    return None