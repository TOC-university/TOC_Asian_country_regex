import re
from .http import fetch

BOLD_IN_BRACKET = re.compile(r"\(.*?<b>([A-Z ]+)</b>.*?\)")
BRACKET = re.compile(r"[> ]\(([A-Z][A-Za-z]+)\)[< ]")
UPPER_COMMA = re.compile(r"\(([A-Z]+),")
RIGHTSIDE_TABLE = re.compile(r"<table class=\"infobox vcard\">.*?</table>", re.S)
IN_PTAG = re.compile(r"<p[^>]*>.*?\b([A-Z]+)\b.*?</p>", re.S)
ATAG = re.compile(r'<a [^>]*>.*?</a>')

TH_TD = re.compile(r"(?is)<th\b[^>]*>\s*Established\b[^<]*</th>\s*<td\b[^>]*>(.*?)</td>")
YRS = re.compile(r"([12]\d{3})")
ESTAB = re.compile(r"established[^\d]{0,50}?([12]\d{3})", re.I)

FACULTY_KEYWORDS = re.compile(
    r"(?i)\b("
    r"Faculty|Faculties|Department|Division|School|Institute|Center|Departments|Organization|Colleges|Schools"
    r"|Facultad|Departamento|División|Escuela|Instituto|Centro|Degrees|Degree|Structure|Training|Programs"
    r")\b"
)
H2 = re.compile(r"<h2 id=[^>]*>(.*?)</h2>")
DL = re.compile(r"<dl><dt>(.*?)</dt></dl>")
DEL_TAG = re.compile(r"<[^>]+?>.*<\/[^>]+>")
H3 = re.compile(r"<h3[^>]*>(.*?)<\/h3>")
LI = re.compile(r"<li>(.*?)<\/li>")
TAG_CONTENT= re.compile(r"<[^>]+?>(.*)<\/[^>]+?>")

INFOCARD_WEBSITE = re.compile(r'(?is)<table class="infobox vcard">.*?Website.*?href="(.*?)".*<\/table>')
REFERENCES_KEYWORDS = re.compile(r"(?i)\b(References|External links)\b")
HREF_HTTP = re.compile(r'(?i)<a[^>]*\bhref\s*=\s*(["\'])(https?://.*?)\1')
BLACKLISTS = re.compile(r"(?i)(?:wiki|article|news|category|trending|[0-9]{2,}|travel|google|pedia|\.com)")
INSTITUTION_KEYWORDS = re.compile(
    r"(?i)\b("
    r"University|College|Institute|Polytechnic|Academy|Faculty|School"
    r"|Universidad|Instituto|Escuela|Politécnico|Tecnológico|Tecnológica"
    r")\b"
)
OVERVIEW = re.compile(r"(?i)\b(Overview|About|History|Introduction|Background|General information)\b")
    
def _is_valid_website(m: str) -> bool:
    after = m.split('://', 1)[1]
    after = after.split('/')
    return not BLACKLISTS.search(m)

def make_abbreviation(path: str) -> str:
    skip_words = {"of", "the", "and", "in", "for"}

    name = path.split('/')[2]
    
    words = re.findall(r"[A-Za-z]+", name)
    
    abbrev_parts = []
    for w in words:
        if w.lower() in skip_words:
            continue
        
        if w.lower().startswith("sh"):
            abbrev_parts.append("Sh")
        else:
            abbrev_parts.append(w[0].upper())
    
    return "".join(abbrev_parts)
def _extract_abbreviate(html, path):
    at = 0
    html_first_section = html.split('<div class=\"mw-heading mw-heading2\">')[0]
    html_first_section = RIGHTSIDE_TABLE.sub("", html_first_section)
    html_first_section = ATAG.sub("", html_first_section)

    in_bracket = BOLD_IN_BRACKET.findall(html_first_section)

    if not in_bracket:
        in_bracket = BRACKET.findall(html_first_section)
        at = 1
    if not in_bracket:
        at = 2
        in_bracket = UPPER_COMMA.findall(html_first_section)
    if not in_bracket:
        at = 3
        in_bracket = IN_PTAG.findall(html_first_section)

    print(f'Abbreviate :          {in_bracket} {at}')

    if len(in_bracket) == 0:
        return f"{make_abbreviation(path)} *"

    return in_bracket[0]

def _extract_established_year(html):
    at = 0
    estab_data = TH_TD.search(html)
    estab_data = estab_data.group(1) if estab_data else None
    estab_data = YRS.search(estab_data) if estab_data else None
    estab_data = estab_data.group(1) if estab_data else None
    if not estab_data:
        at = 1
        estab_data = ESTAB.search(html)
        estab_data = estab_data.group(1) if estab_data else None
    if not estab_data:
        estab_data = 'N/A'
    print(f'Established Year :   {estab_data} {at}')
    return estab_data

def _clean(text):
    text = DEL_TAG.sub("", text)
    text = text.replace('&#93', '')
    text = text.replace('&amp;', '&')
    return text.strip()

def _extract_faculties(html):
    at = 0
    html_sections = html.split('<div class=\"mw-heading mw-heading2\">')
    faculties_sections = []
    addional_sections = []
    for section in html_sections:
        header2 = H2.search(section)
        # print(header2.group(1) if header2 else 'N/A', end=", ")
        if header2 and FACULTY_KEYWORDS.search(header2.group(1)):
            faculties_sections.append(section)
        if header2 and OVERVIEW.search(header2.group(1)):
            addional_sections.append(section)
    if not faculties_sections:
        faculties_sections = addional_sections

    result = []

    for section in faculties_sections:
        facu = DL.findall(section)
        if not facu:
            #
            #TODO: Check if there are any list after each H3
            #
            at = 1
            facu = H3.findall(section)
            if len(facu) < 3 or [f for f in facu if 'graduate' in f.lower()]:
                facu = []
        if not facu:
            at = 2
            lis = LI.findall(section)
            for li in lis:
                content = TAG_CONTENT.search(li)
                if content and not content.group(1).startswith('<'):
                    at = 2.1
                    facu.append(content.group(1))
                else:
                    facu.append(li)

        facu = [_clean(d) for d in facu]
        # print(facu, at)
        result = facu
        break
    # print(f'\nFaculties Sections : {len(faculties_sections)}')
    return result

def _extract_campuses(html):
    # campuses = set()
    # for m in HREF_HTTP.finditer(html):
    #     url = m.group(2)
    #     text = m.group(0)
    #     if _is_valid_website(url) and INSTITUTION_KEYWORDS.search(text):
    #         campuses.add(url)
    # # print(f'Campuses :           {campuses}')
    # return list(campuses)
    pass

def _extract_website(html):
    website = None
    result = INFOCARD_WEBSITE.search(html)
    if result:
        website = result.group(1) 
        print(f'Websites :          {website} (infocard)')
        return website  

    html_sections = html.split('<div class=\"mw-heading mw-heading2\">')
    ref_sections = []
    for section in html_sections:
        header2 = H2.search(section)
        if header2 and REFERENCES_KEYWORDS.search(header2.group(1)):
            ref_sections.append(section)
    print(f'Reference Sections : {len(ref_sections)}')

    for section in ref_sections[::-1]:
        websites = [m.group(2) for m in HREF_HTTP.finditer(section) if _is_valid_website(m.group(2))]
        break
    print(f'Websites :          {websites}')
    print('--------------------------------------')
    website = websites[0] if websites else []
    return website

def extract_universities_detail_from_university_page(path: str) -> dict: ##Abbr EstablishedYrs MainCampus Website
    print('fetching', path)
    html = fetch(path)
    body_part_html = html.split('<body')[1]
    body_part_html = body_part_html.split('\"mw-page-container\"')[1]
    body_part_html = body_part_html.split('\"mw-content-container\"')[1]
    body_part_html = body_part_html.split('\"bodyContent\"')[1]
    # html = html.split('<h2 id="See_also">See also</h2>')[0]
    # html = html.split('<h2 id="References">References</h2>')[0]

    abbreviation = _extract_abbreviate(body_part_html, path)
    estab_data = _extract_established_year(body_part_html)
    campuses = _extract_campuses(body_part_html)
    faculties = _extract_faculties(body_part_html)
    website = _extract_website(body_part_html)

    return {'abbr': abbreviation, 'estab': estab_data, 'campuses': [], 'website': website, 'faculties': faculties}