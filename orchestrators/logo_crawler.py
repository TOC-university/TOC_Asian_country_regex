# File: orchestrators/logo_crawler.py
import os
import re
import html
import asyncio
import httpx
from utils  .http import fetch

STATIC_LOGOS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "logos")
os.makedirs(STATIC_LOGOS_DIR, exist_ok=True)

# Regex patterns
RIGHTSIDE_TABLE = re.compile(r"(?s)<table class=\"infobox vcard\">.*?</table>")
INFOCARD_WEBSITE = re.compile(r'(?is)<table class="infobox vcard">.*?Website.*?href="(.*?)".*</table>')
TH_TD = re.compile(r"(?is)<th[^>]*>\s*Established\s*</th>\s*<td[^>]*>(.*?)</td>")
YRS = re.compile(r"([12]\d{3})")
BOLD_IN_BRACKET = re.compile(r"\(.*?<b>([A-Z ]+)</b>.*?\)")
BRACKET = re.compile(r"</b>[> ].{,10}?\(([A-Z][A-Za-z]+)\)[< ]")
UPPER_COMMA = re.compile(r"</b>.{0,10}?\(([A-Za-z ]+)\),")
BOLD_IN_PTAG = re.compile(r"(?is)(?:short).{,50}?<b>(.*?)</b>")
ABBR_BLACKLIST = re.compile(r"(?i)(?:PhD)")
DEL_TAG_ONLY = re.compile(r"<[^>]+?>")

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

# Extraction functions
def _extract_abbreviation(html_content: str, path: str) -> str:
    html_first_section = RIGHTSIDE_TABLE.sub('', html_content)
    in_bracket = BOLD_IN_BRACKET.findall(html_first_section) or BRACKET.findall(html_first_section) or UPPER_COMMA.findall(html_first_section) or BOLD_IN_PTAG.findall(html_first_section)
    if not in_bracket or ABBR_BLACKLIST.search(in_bracket[0]):
        name = path.split('/')[-1]
        abbrev = ''.join([w[0].upper() for w in re.findall(r'[A-Za-z]+', name)])
        return abbrev
    return in_bracket[0]

def _extract_established_year(html_content: str) -> str:
    data = TH_TD.search(html_content)
    if data:
        year = YRS.search(data.group(1))
        if year:
            return year.group(1)
    return 'N/A'

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

async def extract_university_details(university_name: str) -> dict:
    html_content = await fetch_wikipedia_html(university_name)
    html_body = html_content.split('<body')[1]
    html_body = html_body.split('"mw-page-container"')[1]
    html_body = html_body.split('"mw-content-container"')[1]
    html_body = html_body.split('"bodyContent"')[1]

    abbreviation = _extract_abbreviation(html_body, f'/wiki/{university_name}')
    estab = _extract_established_year(html_body)

    return {'abbr': abbreviation, 'estab': estab}


