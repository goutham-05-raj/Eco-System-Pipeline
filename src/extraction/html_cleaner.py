from __future__ import annotations
from bs4 import BeautifulSoup

REMOVE_TAGS = {
    "script", "style", "nav", "header", "footer",
    "aside", "noscript", "iframe", "svg", "form",
}

BOILERPLATE_CLASSES = {
    "nav", "navbar", "footer", "header", "sidebar", "cookie",
    "advertisement", "social", "share", "related", "recommended",
    "popup", "modal", "banner", "ads",
}


def clean_html(raw_html: str) -> str:
    """Strip non-content elements and return readable plain text."""
    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup.find_all(REMOVE_TAGS):
        tag.decompose()
    for tag in soup.find_all(True):
        classes = " ".join(tag.get("class", []))
        if any(bp in classes.lower() for bp in BOILERPLATE_CLASSES):
            tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def get_soup(raw_html: str) -> BeautifulSoup:
    return BeautifulSoup(raw_html, "lxml")
