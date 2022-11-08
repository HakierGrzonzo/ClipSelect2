import re
from typing import Union
from bs4 import BeautifulSoup as Soup

# Match values like {\foo}
POSITIONING = re.compile(r"{\S+}")

# Match values like `m 1920 18.1 b 34` which are path like svgs
SVG_PATH = re.compile(r"[lbm] (?:(?:-?\d+(?:\.)?\s?)|(?:[lbm])\s?)+")


def extract_text(raw_text: str) -> Union[str, None]:
    # Remove positioning directives
    html_like_text = "".join(POSITIONING.split(raw_text))

    if "<" not in html_like_text:
        # The subtitle does not contain any html tags, so we can return it
        clean_text = html_like_text.strip()
    else:
        # parse html
        soup = Soup(html_like_text, "lxml")
        clean_text = soup.get_text().strip()

    if SVG_PATH.fullmatch(clean_text):
        # the text is svg path, we skip it
        return None

    return clean_text
