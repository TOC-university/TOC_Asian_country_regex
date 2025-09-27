import re
from .http import fetch

AFTER_FULLNAME = re.compile(r'\(\s*<b>([A-Z]{2,6})</b>\s*\)')
BRACKET = re.compile(r"\(([A-Z]+)\)")
BOLD = re.compile(r"<b>([A-Z]+?)</b>")


TH_TD = re.compile(r"(?is)<th\b[^>]*>\s*Established\b[^<]*</th>\s*<td\b[^>]*>(.*?)</td>")
YRS = re.compile(r"([12]\d{3})")
ESTAB = re.compile(r"established[^\d]{0,50}?([12]\d{3})", re.I)
HREF_HTTP = re.compile(r'(?i)<a[^>]*\bhref\s*=\s*(["\'])(https?://.*?)\1')
KEYWORDS = re.compile(r"(?i)(?:wiki|\.com|\?|&|\.net)")
INSTITUTION_KEYWORDS = re.compile(
    r"(?i)\b("
    r"University|College|Institute|Polytechnic|Academy|Faculty|School"
    r"|Universidad|Instituto|Escuela|Politécnico|Tecnológico|Tecnológica"
    r")\b"
)
    
def _is_valid_website(m: str) -> bool:
    after = m.split('://', 1)[1]
    after = after.split('/')

    return (len(after) == 1 or after[1] == '' or after[1] == 'en') and not KEYWORDS.search(m)

def extract_universities_detail_from_university_page(path: str) -> dict: ##Abbr EstablishedYrs MainCampus Website
    print('fetching', path)
    html = fetch(path)
    # html = html.split('<h2 id="See_also">See also</h2>')[0]
    # html = html.split('<h2 id="References">References</h2>')[0]

    in_bracket = BRACKET.findall(html)
    in_bracket = [b for b in in_bracket if b not in ['PDF', 'UTC'] and b.isalpha()]
    if not in_bracket:
        in_bracket = BOLD.findall(html)  
    in_bracket = [b for b in in_bracket if b not in ['PDF', 'UTC'] and b.isalpha()]
    
    if len(in_bracket) == 0: # not found case
        in_bracket.append(''.join([word[0] for word in path.split('/')[2].split('_') if word[0].isupper()]) + ' *') # make abbreviation from slug
    abbreviation = in_bracket[0]
    
    estab_data = TH_TD.search(html)
    estab_data = estab_data.group(1) if estab_data else None
    estab_data = YRS.search(estab_data) if estab_data else None
    estab_data = estab_data.group(1) if estab_data else None
    if not estab_data:
        estab_data = ESTAB.search(html)
        estab_data = estab_data.group(1) if estab_data else None
    if not estab_data:
        estab_data = 'N/A'

    campuses = []

    faculty = []


    websites = [m.group(2) for m in HREF_HTTP.finditer(html) if _is_valid_website(m.group(2))]
    website = websites[0] if websites else None
    # website = HREF_HTTP.search(html).group(2) if HREF_HTTP.search(html) else None
    print(abbreviation)
    print(estab_data)
    print(websites)

    return {'abbr': abbreviation, 'estab': estab_data, 'campuses': campuses, 'website': website, 'faculty': faculty}