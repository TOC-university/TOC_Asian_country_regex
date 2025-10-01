import re
import html
from .http import fetch

RIGHTSIDE_TABLE = re.compile(r"(?s)<table class=\"infobox vcard\">.*?</table>") #sub
ATAG = re.compile(r'<a [^>]*>.*?</a>') #sub
BOLD_IN_BRACKET = re.compile(r"\(.*?<b>([A-Z ]+)</b>.*?\)")
BRACKET = re.compile(r"[> ]\(([A-Z][A-Za-z]+)\)[< ]")
UPPER_COMMA = re.compile(r"\(([A-Z]+),")
BOLD_IN_PTAG = re.compile(r"(?is)(?:short).{,50}?<b>(.*?)<\/b>")
ABBR_BLACKLIST = re.compile(r"(?i)(?:PhD)")

TH_TD = re.compile(r"(?is)<th\b[^>]*>\s*Established\b[^<]*</th>\s*<td\b[^>]*>(.*?)</td>")
YRS = re.compile(r"([12]\d{3})")
ESTAB = re.compile(r"(?i)established[^\d]{0,50}?([12]\d{3})")

FACULTY_KEYWORDS = re.compile(
    r"(?i)\b("
    r"Faculty|Faculties|Department|Division|School|Institute|Center|Departments|Colleges|Schools|organisation"
    r"|Facultad|Departamento|División|Escuela|Instituto|Centro|Degrees|Degree|Structure|Training|Programs"
    r")\b"
)
H2 = re.compile(r"<h2 id=[^>]*>(.*?)</h2>")
DL = re.compile(r"<dl><dt>(.*?)</dt></dl>")
DEL_TAG = re.compile(r"(?s)<[^>]+?>.*<\/[^>]+>")
H3 = re.compile(r"<h3[^>]*>(.*?)<\/h3>")
LI = re.compile(r"(?s)<li>(.*?)<\/li>")
TAG_CONTENT = re.compile(r"<(\w+)[^>]*>(.*?)<\/\1>")
PTAG_KEYWORD = re.compile(r"(?is)<p>(.*?(?:such).*?)<\/p>")
FACULTY_BLACKLIST = re.compile(r"(?i)(?:affiliate|alumni|notable)")

INFOCARD_WEBSITE = re.compile(r'(?is)<table class="infobox vcard">.*?Website.*?href="(.*?)".*<\/table>')
REFERENCES_KEYWORDS = re.compile(r"(?i)\b(References|External links)\b")
HREF_HTTP = re.compile(r'(?i)<a[^>]*\bhref\s*=\s*(["\'])(https?://.*?)\1')
BLACKLISTS = re.compile(r"(?i)(?:wiki|article|news|category|trending|[0-9]{2,}|travel|google|pedia|\.com)")
OVERVIEW = re.compile(r"(?i)\b(Overview|About|History|Introduction|Background|General information)\b")

CAMPUS_KEYWORDS = re.compile(r"(?i)\b(Campuses|Campus|Branches|Locations|Location|Main campus|Other campuses)")
TABLE = re.compile(r'(?is)<table class="infobox vcard">(.*?)</table>')
INFOCARD_LOCATION = re.compile(r'(?is)"(?:locality|country-name|street-address)">(.*?)</div>')
BRANCH = re.compile(r"<(\w+)[^>]*>(.*?)<\/\1>([^\.]+?)[\. ]+")
DEL_TAG_ONLY = re.compile(r"<[^>]+?>")
CAMPUS_BLACKLIST = re.compile(r"(?i)(?:building|city|cities|facilities|facility|centre|court)")
    
test1 = re.compile(r"(?s)<ul><li>(.*?)(?=(?:<\/li><\/ul>))")


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

    if not in_bracket or ABBR_BLACKLIST.search(in_bracket[0] if in_bracket else ''):
        in_bracket = BRACKET.findall(html_first_section)
        at = 1
    if not in_bracket or ABBR_BLACKLIST.search(in_bracket[0] if in_bracket else ''):
        at = 2
        in_bracket = UPPER_COMMA.findall(html_first_section)
    if not in_bracket or ABBR_BLACKLIST.search(in_bracket[0] if in_bracket else ''):
        at = 3
        in_bracket = BOLD_IN_PTAG.findall(html_first_section)

#/wiki/Nation_University_(Thailand)
#/wiki/Thongsuk_College
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
    # print(f'Established Year :   {estab_data} {at}')
    return estab_data

def _clean(text):
    text = DEL_TAG_ONLY.sub('', text).strip()
    text = html.unescape(text)
    text = re.sub(r"\[\d+.*?\]", "", text).strip()
    text = DEL_TAG.sub("", text)
    text = text.replace('&#93', '')
    text = text.replace('&amp;', '&')
    text = text.replace('.', '')
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def _extract_faculties(html):
    at = 0
    html_sections = html.split('<div class=\"mw-heading mw-heading2\">')
    faculties_sections = []
    addional_sections = []
    for section in html_sections:
        if FACULTY_BLACKLIST.search(section):
            continue
        header2 = H2.search(section)
        # print(header2.group(1) if header2 else 'N/A', end=", ")
        if header2 and FACULTY_KEYWORDS.search(header2.group(1)):
            faculties_sections.append(section)
        if header2 and OVERVIEW.search(header2.group(1)):
            addional_sections.append(section)
    # if not faculties_sections:
    #     faculties_sections = addional_sections

    result = []

    for section in faculties_sections:
        facu = DL.findall(section)
        if not facu:
            at = 1
            facu = [_clean(s) for s in H3.findall(section)]
            if len(facu) < 3 or [f for f in facu if 'graduate' in f.lower()]:
                facu = []
        if not facu:
            at = 2
            lis = LI.findall(section)

            lis = _get_parent_list_of_list(lis, section)
            for li in lis:    
                if '>' not in DEL_TAG.sub("", li):
                    facu.append(_clean(DEL_TAG_ONLY.sub("", li).split(":")[0]))
                else:
                    content = TAG_CONTENT.search(li)
                    if content:
                        at = 2.1
                        facu.append(_clean(content.group(2))) 
                    else:
                        facu.append(_clean(li))
        if not facu:
            at = 3
            ptags = PTAG_KEYWORD.findall(section)
            if ptags:
                needed_ptag = DEL_TAG_ONLY.sub("|", ptags[0])
                needed_ptag = [_clean(s) for s in needed_ptag.split("|") if not re.search(r"(?i)(?:,|such|and|\.|\n)", s) ]
                facu = needed_ptag

        facu = [_clean(d) for d in facu]
        result = facu
        break
    print(f'Faculties  :          {result} {at}')
    print(f'\nFaculties Sections : {len(faculties_sections)}')
    return result

def _extract_campuses(html):
    at = 0
    html_sections = html.split('<div class=\"mw-heading mw-heading2\">')
    sections = []
    result = []
    for section in html_sections:
        header2 = H2.search(section)
        if header2 and CAMPUS_KEYWORDS.search(header2.group(1)):
            sections.append(section)

    section = sections[0] if sections else ''
    before_h3 = section.split('<h3')[0]
    if '<li' not in before_h3:     #Campus as H3
        print('pass H3')    
        h3 = H3.findall(section)
        for content in h3:
            result.append(f'{_clean(DEL_TAG_ONLY.sub('', content))} campus')

    if not result:              #Campus as list
        lis = LI.findall(before_h3)
        at = 1
        for li in lis:
            if CAMPUS_BLACKLIST.search(li):
                continue
            print(li)
            content = TAG_CONTENT.search(li)
            if content:    
                string = content.group(2) if 'branch' in content.group(2).lower() else f'{content.group(2)} branch'
            else:
                string = li if 'branch' in li.lower() else f'{li} branch'
            
            result.append(_clean(string))

    if not result:          #Campus as paragraph
        h2_content = []
        for section in sections:
            h2_content = H2.findall(section)    
            for content in h2_content: 
                at = 2
                if not CAMPUS_BLACKLIST.search(content):
                    result.append(_clean(content))  
        
    print(f'Campus     :          {result} {at}')
    return result

def _extract_location(html):
    location = None
    result = TABLE.search(html)
    if result:
        table_html = result.group(1)
        result = INFOCARD_LOCATION.findall(table_html)
        result = [_clean(r) for r in result]
        print(f'Location (infocard) : {[_clean(r) for r in result]}')

        return ', '.join(result)
    return 'N/A'

def _extract_website(html):
    website = None
    websites = []
    result = INFOCARD_WEBSITE.search(html)
    if result:
        website = result.group(1) 
        # print(f'Websites :          {website} (infocard)')
        return website  

    html_sections = html.split('<div class=\"mw-heading mw-heading2\">')
    ref_sections = []
    for section in html_sections:
        header2 = H2.search(section)
        if header2 and REFERENCES_KEYWORDS.search(header2.group(1)):
            ref_sections.append(section)
    # print(f'Reference Sections : {len(ref_sections)}')

    for section in ref_sections[::-1]:
        websites = [m.group(2) for m in HREF_HTTP.finditer(section) if _is_valid_website(m.group(2))]
        break
    # print(f'Websites :          {websites}')
    # print('--------------------------------------')
    website = websites[0] if websites else []
    return website

def _get_parent_list_of_list(lis, section):
    result = []
    parent_count = 0
    for li in lis:
        if '<' in li:
            ul_count = li.count('<ul>')
            if ul_count > parent_count:
                parent_count = ul_count
            else:
                pass
    return lis

def extract_universities_detail_from_university_page(path: str, needed_data: list = []) -> dict: ##Abbr EstablishedYrs MainCampus Website
    if not needed_data:
        needed_data = ['abbreviate', 'estab', 'location', 'campuses', 'website', 'faculties']   
    print('fetching', path)
    html = fetch(path)
    body_part_html = html.split('<body')[1]
    body_part_html = body_part_html.split('\"mw-page-container\"')[1]
    body_part_html = body_part_html.split('\"mw-content-container\"')[1]
    body_part_html = body_part_html.split('\"bodyContent\"')[1]
    # html = html.split('<h2 id="See_also">See also</h2>')[0]
    # html = html.split('<h2 id="References">References</h2>')[0]
    abbreviation = ''
    estab_data = ''
    location = ''
    campuses = []
    website = ''
    faculties = []
    if 'abbreviate' in needed_data:
        abbreviation = _extract_abbreviate(body_part_html, path)
    if 'estab' in needed_data:
        estab_data = _extract_established_year(body_part_html)
    if 'campuses' in needed_data:
        campuses = _extract_campuses(body_part_html)
    if 'faculties' in needed_data:
        faculties = _extract_faculties(body_part_html)
    if 'website' in needed_data:
        website = _extract_website(body_part_html)
    if 'location' in needed_data:
        location = _extract_location(body_part_html)
    needed_data = []
    return {'abbr': abbreviation, 'estab': estab_data, 'location': location, 'campuses': campuses, 'website': website, 'faculties': faculties}